import streamlit as st
from wizzard_game import WizardGame


st.set_page_config(
    page_title="Wizard Score Calculator",
    page_icon="🃏",
    layout="wide",
)


# Create one WizardGame object for this browser session.
if "wizard_game" not in st.session_state:
    st.session_state.wizard_game = WizardGame()

# Give the stored game a shorter name.
game: WizardGame = st.session_state.wizard_game


st.title("🧙 Wizard Scorekeeper")


# ---------------------------------
# Add players
# ---------------------------------

st.header("Players")

if game.rounds_played == 0:
    with st.form(
        "add_player_form",
        clear_on_submit=True,
    ):
        player_name = st.text_input(
            "Player name",
            placeholder="Enter a player name",
        )

        add_player = st.form_submit_button("Add player")

        if add_player:
            try:
                game.add_player(player_name)
                st.rerun()

            except ValueError as error:
                st.error(str(error))
else:
    st.caption(
        "The player list is locked because the game has started."
    )


if game.players and game.rounds_played ==0:
    st.write("**Current players:**")

    for player in game.players:
        st.write(f"- {player}")
elif game.players and game.rounds_played > 0:
    pass
else:
    st.info("Add at least two players to begin.")


# ---------------------------------
# Enter round scores
# ---------------------------------

if len(game.players) >= 2:
    st.divider()
    st.header(f"Round {game.next_round}")

    with st.form(f"round_form_{game.next_round}"):
        bets: dict[str, int] = {}
        tricks_got: dict[str, int] = {}

        # Headings
        with st.container(
            horizontal=True,
            vertical_alignment="center",
            gap=None,
        ):
            st.markdown("**Player**", width=75)
            st.markdown("**Bet**", width=125)
            st.markdown("**Got**", width=125)

        # Player rows
        for player_number, player in enumerate(game.players):
            with st.container(
                horizontal=True,
                vertical_alignment="center",
                gap=None,
            ):
                st.markdown(
                    f"**{player}**",
                    width=75,
                )

                bets[player] = int(
                    st.number_input(
                        label=f"{player} bet",
                        min_value=0,
                        max_value=game.next_round,
                        value=0,
                        step=1,
                        format="%d",
                        key=(
                            f"bet_{game.next_round}_"
                            f"{player_number}"
                        ),
                        label_visibility="collapsed",
                        width=125,
                    )
                )

                tricks_got[player] = int(
                    st.number_input(
                        label=f"{player} got",
                        min_value=0,
                        max_value=game.next_round,
                        value=0,
                        step=1,
                        format="%d",
                        key=(
                            f"got_{game.next_round}_"
                            f"{player_number}"
                        ),
                        label_visibility="collapsed",
                        width=125,
                    )
                )

        save_round = st.form_submit_button(
            "Save round",
            type="primary",
            width="stretch",
        )

        if save_round:
            try:
                game.add_round(
                    bets=bets,
                    tricks_got=tricks_got,
                )
                st.rerun()

            except ValueError as error:
                st.error(str(error))


# ---------------------------------
# Current standings
# ---------------------------------

if not game.scores.empty:
    st.divider()
    st.header("Current standings")

    leaderboard = game.leaderboard()

    st.dataframe(
        leaderboard,
        hide_index=True,
        use_container_width=True,
    )

    leader = leaderboard.iloc[0]

    if len(leaderboard) >= 2:
        second_place = leaderboard.iloc[1]

        lead_amount = int(
            leader["Running Total"]
            - second_place["Running Total"]
        )
    else:
        lead_amount = 0

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Current leader",
        leader["Player"],
    )

    metric2.metric(
        "Leader's score",
        int(leader["Running Total"]),
    )

    metric3.metric(
        "In the lead by",
        lead_amount,
    )
    
    metric4.metric(
        "Runner up",
        second_place["Player"] if len(leaderboard) >= 2 else "N/A",
    )


    # ---------------------------------
    # Score history
    # ---------------------------------

    st.header("Score history")

    score_history = game.score_history(
        value="Running Total"
    )

    st.dataframe(
        score_history,
        hide_index=True,
        use_container_width=True,
    )


    # ---------------------------------
    # Score chart
    # ---------------------------------

    chart_data = score_history.set_index("Round")

    st.header("Running totals")

    st.line_chart(chart_data)
    # ---------------------------------
    # Z-score chart
    # ---------------------------------

    st.header("Player z-scores")

    z_score_data = game.z_scores()

    z_score_chart = (
        z_score_data[
            ["Player", "Z-Score"]
        ]
        .set_index("Player")
    )

    st.bar_chart(z_score_chart)

    st.caption(
        "Positive values are above the player average. "
        "Negative values are below the player average."
    )
    # ---------------------------------
    # Bid accuracy
    # ---------------------------------

    st.header("Bid accuracy")

    accuracy_data = game.bid_accuracy()

    accuracy_columns = st.columns(
        len(accuracy_data)
    )

    for column, (_, player) in zip(
        accuracy_columns,
        accuracy_data.iterrows(),
    ):
        column.metric(
            label=player["Player"],
            value=f"{player['Bid Accuracy']:.1f}%",
            help=(
                f"{int(player['Correct Bids'])} correct bids "
                f"out of {int(player['Rounds Played'])} rounds"
            ),
        )


    # ---------------------------------
    # Game controls
    # ---------------------------------

    undo_column, reset_column = st.columns(2)

    if undo_column.button(
        "Undo last round",
        use_container_width=True,
    ):
        game.undo_last_round()
        st.rerun()

    if reset_column.button(
        "Reset game",
        use_container_width=True,
    ):
        game.reset()
        st.rerun()

elif game.players:
    st.divider()

    if st.button(
        "Reset players",
        use_container_width=True,
    ):
        game.reset()
        st.rerun()