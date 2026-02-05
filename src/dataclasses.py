"""
Data classes for American Padel Tournament.
Contains Match and Calendar Pydantic models.
"""

import numpy as np
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional

from .utils import is_valid_match, get_players_from_vector


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_minimum_players_for_courts(n_courts: int) -> int:
    """
    Calculate the minimum number of players needed for n_courts.

    With n_courts, we need at least enough players to have different
    players in each simultaneous match. Minimum is 4 players per court,
    but they can share across courts.

    Args:
        n_courts: Number of courts available

    Returns:
        Minimum number of players needed
    """
    # With 1 court: 4 players minimum
    # With 2 courts: 8 players minimum (all 8 can play simultaneously)
    # With n courts: 4*n players minimum for full utilization
    return 4 * n_courts


def can_use_multiple_courts(n_players: int, n_courts: int) -> bool:
    """
    Check if the number of players is appropriate for using multiple courts.

    Args:
        n_players: Number of players in the tournament
        n_courts: Number of courts to use

    Returns:
        True if configuration is valid, False otherwise
    """
    if n_courts < 1:
        return False
    if n_courts == 1:
        return n_players >= 4
    # For multiple courts, we need at least 4*n_courts players
    # to have all courts playing with different players
    return n_players >= get_minimum_players_for_courts(n_courts)


# ============================================================================
# MATCH CLASS
# ============================================================================


class Match(BaseModel):
    """
    Represents a single match with its vector representation.
    Uses Pydantic for automatic validation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    match_vector: np.ndarray
    n_players: int

    @field_validator("match_vector")
    @classmethod
    def validate_match_vector(cls, v):
        """Validate that match has exactly 4 different players."""
        if not is_valid_match(v):
            raise ValueError(
                "Invalid match: must have exactly 4 different players (2 per team)"
            )
        return v

    def is_valid(self) -> bool:
        """Check if match is valid."""
        return is_valid_match(self.match_vector)

    def get_players(self) -> list[int]:
        """
        Get list of player indices participating in this match.

        Returns:
            List of 4 player indices
        """
        players = []
        n = self.n_players

        # Check team 1
        for i in range(n):
            if self.match_vector[i] == 1:
                players.append(i)

        # Check team 2
        for i in range(n):
            if self.match_vector[n + i] == 1:
                if (
                    i not in players
                ):  # Avoid duplicates (shouldn't happen in valid match)
                    players.append(i)

        return players

    def get_teams(self) -> tuple[list[int], list[int]]:
        """
        Get the two teams as separate lists.

        Returns:
            Tuple of (team1, team2) where each is a list of player indices
        """
        n = self.n_players
        team1 = []
        team2 = []

        # Get team 1
        for i in range(n):
            if self.match_vector[i] == 1:
                team1.append(i)

        # Get team 2
        for i in range(n):
            if self.match_vector[n + i] == 1:
                team2.append(i)

        return team1, team2

    def __str__(self) -> str:
        """String representation of match."""
        team1, team2 = self.get_teams()

        # Convert indices to letters (A, B, C, ...)
        def idx_to_letter(idx):
            return chr(ord("A") + idx)

        team1_str = ",".join(idx_to_letter(p) for p in team1)
        team2_str = ",".join(idx_to_letter(p) for p in team2)

        return f"({team1_str}) vs ({team2_str})"


# ============================================================================
# CALENDAR CLASS
# ============================================================================


class Calendar(BaseModel):
    """
    Represents a complete tournament calendar.
    Uses Pydantic for automatic validation.

    With n_courts > 1, matches are grouped into rounds where multiple matches
    can be played simultaneously. Each round contains up to n_courts matches.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    matches: np.ndarray  # Shape: (n_matches, 2 * n_players)
    n_players: int
    n_courts: int = 1  # Number of courts available (default: 1 = sequential play)

    @field_validator("matches")
    @classmethod
    def validate_all_matches(cls, v):
        """Validate that all matches are valid."""
        if len(v) == 0:
            return v  # Empty calendar is valid

        for i, match_vector in enumerate(v):
            if not is_valid_match(match_vector):
                raise ValueError(f"Calendar contains invalid match at index {i}")
        return v

    def __len__(self) -> int:
        """Return number of matches in calendar."""
        return len(self.matches)

    def get_total_rounds(self) -> int:
        """
        Get the total number of rounds in the calendar.

        With n_courts courts, each round contains up to n_courts matches.

        Returns:
            Total number of rounds
        """
        if len(self.matches) == 0:
            return 0
        # Ceiling division to get number of rounds
        return (len(self.matches) + self.n_courts - 1) // self.n_courts

    def get_round_for_match(self, match_index: int) -> int:
        """
        Get the round number for a specific match.

        Args:
            match_index: Match index (0-based)

        Returns:
            Round number (1-based)
        """
        if match_index < 0 or match_index >= len(self.matches):
            raise IndexError(f"Match index {match_index} out of range")
        return (match_index // self.n_courts) + 1

    def get_matches_in_round(self, round_num: int) -> list[int]:
        """
        Get the match indices that belong to a specific round.

        Args:
            round_num: Round number (1-based)

        Returns:
            List of match indices in that round
        """
        if round_num < 1:
            raise ValueError(f"Round number must be >= 1, got {round_num}")

        start_idx = (round_num - 1) * self.n_courts
        end_idx = min(start_idx + self.n_courts, len(self.matches))

        return list(range(start_idx, end_idx))

    def get_match(self, index: int) -> Match:
        """
        Get a specific match by index.

        Args:
            index: Match index (0-based)

        Returns:
            Match object

        Raises:
            IndexError: If index is out of bounds
        """
        if index < 0 or index >= len(self.matches):
            raise IndexError(f"Match index {index} out of range")

        return Match(match_vector=self.matches[index], n_players=self.n_players)

    def is_valid(self) -> bool:
        """Check if all matches in calendar are valid."""
        for match_vector in self.matches:
            if not is_valid_match(match_vector):
                return False
        return True

    def has_round_conflicts(self) -> bool:
        """
        Check if any player appears in multiple matches within the same round.

        A round conflict occurs when a player is scheduled to play in two
        different matches that happen simultaneously on different courts.

        Returns:
            True if there are conflicts, False otherwise
        """
        if self.n_courts <= 1:
            return False  # No conflicts possible with single court

        for round_num in range(1, self.get_total_rounds() + 1):
            match_indices = self.get_matches_in_round(round_num)
            players_in_round = set()

            for match_idx in match_indices:
                match = self.get_match(match_idx)
                players = match.get_players()

                for player in players:
                    if player in players_in_round:
                        return True  # Conflict found
                    players_in_round.add(player)

        return False

    def get_round_conflicts(self) -> list[tuple[int, int, int]]:
        """
        Get detailed information about round conflicts.

        Returns:
            List of tuples (round_num, player_idx, match_count) for each conflict
        """
        conflicts = []

        if self.n_courts <= 1:
            return conflicts  # No conflicts possible with single court

        for round_num in range(1, self.get_total_rounds() + 1):
            match_indices = self.get_matches_in_round(round_num)
            player_match_count = {}

            for match_idx in match_indices:
                match = self.get_match(match_idx)
                players = match.get_players()

                for player in players:
                    player_match_count[player] = player_match_count.get(player, 0) + 1

            # Find players with multiple matches in this round
            for player, count in player_match_count.items():
                if count > 1:
                    conflicts.append((round_num, player, count))

        return conflicts

    def get_matches_per_player(self) -> dict[int, int]:
        """
        Count how many matches each player plays.

        Uses vectorized numpy operations for performance.

        Returns:
            Dictionary mapping player_index -> match_count
        """
        # Vectorized approach: sum across all matches
        # Each match has 2 players in team1 and 2 in team2
        team1_counts = self.matches[:, :self.n_players].sum(axis=0)
        team2_counts = self.matches[:, self.n_players:].sum(axis=0)
        total_counts = team1_counts + team2_counts

        # Convert to dict for backward compatibility
        return {i: int(count) for i, count in enumerate(total_counts)}

    def get_waiting_rounds_per_player(self) -> dict[int, list[int]]:
        """
        Calculate waiting rounds (gaps) between matches for each player.

        With n_courts > 1, this calculates gaps in terms of rounds, not matches.
        A player is considered to play in a round if they have at least one
        match in that round.

        Returns:
            Dictionary mapping player_index -> list of gaps between consecutive rounds played
        """
        waiting_rounds = {i: [] for i in range(self.n_players)}

        for player in range(self.n_players):
            # Find all rounds where this player plays (optimized)
            rounds_played = set()
            for i, match_vector in enumerate(self.matches):
                players = get_players_from_vector(match_vector, self.n_players)
                if player in players:
                    round_num = self.get_round_for_match(i)
                    rounds_played.add(round_num)

            # Sort rounds and calculate gaps
            sorted_rounds = sorted(rounds_played)
            for i in range(len(sorted_rounds) - 1):
                # Gap is the number of rounds between consecutive plays
                gap = sorted_rounds[i + 1] - sorted_rounds[i] - 1
                waiting_rounds[player].append(gap)

        return waiting_rounds

    def get_waiting_matches_per_player(self) -> dict[int, list[int]]:
        """
        Calculate waiting in terms of individual matches (legacy behavior).

        This is the original waiting calculation based on match indices,
        not rounds. Useful for comparison when n_courts > 1.

        Returns:
            Dictionary mapping player_index -> list of gaps between consecutive matches
        """
        waiting_matches = {i: [] for i in range(self.n_players)}

        for player in range(self.n_players):
            # Find all match indices where this player plays (optimized)
            match_indices = []
            for i, match_vector in enumerate(self.matches):
                players = get_players_from_vector(match_vector, self.n_players)
                if player in players:
                    match_indices.append(i)

            # Calculate gaps between consecutive matches
            for i in range(len(match_indices) - 1):
                gap = match_indices[i + 1] - match_indices[i] - 1
                waiting_matches[player].append(gap)

        return waiting_matches
