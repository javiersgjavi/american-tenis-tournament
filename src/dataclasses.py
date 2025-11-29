"""
Data classes for American Padel Tournament.
Contains Match and Calendar Pydantic models.
"""

import numpy as np
from pydantic import BaseModel, field_validator, ConfigDict

from .utils import is_valid_match


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
    
    @field_validator('match_vector')
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
                if i not in players:  # Avoid duplicates (shouldn't happen in valid match)
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
            return chr(ord('A') + idx)
        
        team1_str = ','.join(idx_to_letter(p) for p in team1)
        team2_str = ','.join(idx_to_letter(p) for p in team2)
        
        return f"({team1_str}) vs ({team2_str})"


# ============================================================================
# CALENDAR CLASS
# ============================================================================

class Calendar(BaseModel):
    """
    Represents a complete tournament calendar.
    Uses Pydantic for automatic validation.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    matches: np.ndarray  # Shape: (n_matches, 2 * n_players)
    n_players: int
    
    @field_validator('matches')
    @classmethod
    def validate_all_matches(cls, v):
        """Validate that all matches are valid."""
        if len(v) == 0:
            return v  # Empty calendar is valid
        
        for i, match_vector in enumerate(v):
            if not is_valid_match(match_vector):
                raise ValueError(
                    f"Calendar contains invalid match at index {i}"
                )
        return v
    
    def __len__(self) -> int:
        """Return number of matches in calendar."""
        return len(self.matches)
    
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
        
        return Match(
            match_vector=self.matches[index],
            n_players=self.n_players
        )
    
    def is_valid(self) -> bool:
        """Check if all matches in calendar are valid."""
        for match_vector in self.matches:
            if not is_valid_match(match_vector):
                return False
        return True
    
    def get_matches_per_player(self) -> dict[int, int]:
        """
        Count how many matches each player plays.
        
        Returns:
            Dictionary mapping player_index -> match_count
        """
        counts = {i: 0 for i in range(self.n_players)}
        
        for match_vector in self.matches:
            match = Match(match_vector=match_vector, n_players=self.n_players)
            players = match.get_players()
            for player in players:
                counts[player] += 1
        
        return counts
    
    def get_waiting_rounds_per_player(self) -> dict[int, list[int]]:
        """
        Calculate waiting rounds (gaps) between matches for each player.
        
        Returns:
            Dictionary mapping player_index -> list of gaps between consecutive matches
        """
        waiting_rounds = {i: [] for i in range(self.n_players)}
        
        for player in range(self.n_players):
            # Find all match indices where this player plays
            match_indices = []
            for i, match_vector in enumerate(self.matches):
                match = Match(match_vector=match_vector, n_players=self.n_players)
                if player in match.get_players():
                    match_indices.append(i)
            
            # Calculate gaps between consecutive matches
            for i in range(len(match_indices) - 1):
                gap = match_indices[i + 1] - match_indices[i] - 1
                waiting_rounds[player].append(gap)
        
        return waiting_rounds

