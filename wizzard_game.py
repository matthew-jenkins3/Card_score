import pandas as pd

class WizardGame:
    """Stores the players, scores, and rules for one Wizard game."""

    SCORE_COLUMNS = [
        "Round",
        "Player",
        "Bet",
        "Got",
        "Round Score",
        "Running Total",
    ]

    def __init__(self) -> None:
        self.players: list[str] = []
        self.scores = pd.DataFrame(columns=self.SCORE_COLUMNS)

    @staticmethod
    def calculate_score(bet: int, got: int) -> int:
        """Calculate one player's score for a round."""
        if bet == got:
            return 20 + (10 * got)

        return -10 * abs(bet - got)

    @property
    def rounds_played(self) -> int:
        """Return the number of completed rounds."""
        if self.scores.empty:
            return 0

        return int(self.scores["Round"].max())

    @property
    def next_round(self) -> int:
        """Return the next round number."""
        return self.rounds_played + 1

    def add_player(self, name: str) -> None:
        """Add a player before the first round begins."""
        cleaned_name = name.strip()

        if not cleaned_name:
            raise ValueError("Enter a player name.")

        if self.rounds_played > 0:
            raise ValueError(
                "Players cannot be added after the game begins."
            )

        existing_names = [
            player.lower()
            for player in self.players
        ]

        if cleaned_name.lower() in existing_names:
            raise ValueError("That player has already been added.")

        self.players.append(cleaned_name)

    def total_for(self, player: str) -> int:
        """Return one player's current total."""
        player_scores = self.scores[
            self.scores["Player"] == player
        ]

        if player_scores.empty:
            return 0

        return int(player_scores["Round Score"].sum())

    def add_round(
        self,
        bets: dict[str, int],
        tricks_got: dict[str, int],
    ) -> None:
        """Calculate and save a complete round."""
        if len(self.players) < 2:
            raise ValueError("Add at least two players.")

        round_number = self.next_round
        total_tricks = sum(tricks_got.values())

        if total_tricks != round_number:
            raise ValueError(
                f"The Got values must total {round_number}. "
                f"They currently total {total_tricks}."
            )

        new_rows = []

        for player in self.players:
            bet = bets[player]
            got = tricks_got[player]

            round_score = self.calculate_score(
                bet=bet,
                got=got,
            )

            running_total = (
                self.total_for(player) + round_score
            )

            new_rows.append(
                {
                    "Round": round_number,
                    "Player": player,
                    "Bet": bet,
                    "Got": got,
                    "Round Score": round_score,
                    "Running Total": running_total,
                }
            )

        new_scores = pd.DataFrame(new_rows)

        if self.scores.empty:
            self.scores = new_scores
        else:
            self.scores = pd.concat(
                [self.scores, new_scores],
                ignore_index=True,
            )

    def leaderboard(self) -> pd.DataFrame:
        """Return players ordered by their current totals."""
        rows = [
            {
                "Player": player,
                "Running Total": self.total_for(player),
            }
            for player in self.players
        ]

        leaderboard = pd.DataFrame(rows)

        if leaderboard.empty:
            return leaderboard

        leaderboard = leaderboard.sort_values(
            by="Running Total",
            ascending=False,
        ).reset_index(drop=True)

        leaderboard.insert(
            0,
            "Position",
            range(1, len(leaderboard) + 1),
        )

        return leaderboard

    def score_history(
        self,
        value: str = "Running Total",
    ) -> pd.DataFrame:
        """
        Return rounds as rows and player names as columns.

        value can be:
        - "Running Total"
        - "Round Score"
        - "Bet"
        - "Got"
        """
        if self.scores.empty:
            return pd.DataFrame()

        history = self.scores.pivot(
            index="Round",
            columns="Player",
            values=value,
        )

        # Preserve the order in which players were added.
        history = history.reindex(columns=self.players)

        history = history.reset_index()
        history.columns.name = None

        return history

    def undo_last_round(self) -> None:
        """Remove the most recently entered round."""
        if self.scores.empty:
            return

        last_round = self.rounds_played

        self.scores = (
            self.scores[
                self.scores["Round"] != last_round
            ]
            .copy()
            .reset_index(drop=True)
        )

    def reset(self) -> None:
        """Reset the entire game."""
        self.players = []
        self.scores = pd.DataFrame(
            columns=self.SCORE_COLUMNS
        )