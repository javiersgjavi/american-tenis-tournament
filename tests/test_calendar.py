"""
Tests for Calendar class.
Following TDD methodology - these tests define the expected behavior.
"""

import pytest
import numpy as np
from src.genetic_algorithm import Calendar, Match, generate_random_match


class TestCalendar:
    """Test the Calendar class."""
    
    def test_create_valid_calendar(self):
        """Test creating a valid Calendar instance."""
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 1, 1, 0],  # (A,D) vs (B,C)
        ])
        calendar = Calendar(matches=matches, n_players=4)
        assert calendar is not None
    
    def test_create_calendar_with_invalid_match_raises_error(self):
        """Test that creating calendar with invalid match raises ValidationError."""
        from pydantic import ValidationError
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # Valid
            [1, 1, 1, 0, 0, 0, 1, 0],  # Invalid: 3 vs 1
        ])
        with pytest.raises(ValidationError):
            Calendar(matches=matches, n_players=4)
    
    def test_len_method(self):
        """Test __len__ method returns number of matches."""
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 1, 1, 0],  # (A,D) vs (B,C)
            [0, 1, 1, 0, 0, 0, 0, 1],  # (B,C) vs (D) - INVALID: only 3 players
        ])
        # Fix: proper 4 players in match 3
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 1, 1, 0],  # (A,D) vs (B,C)
            [0, 1, 1, 0, 1, 0, 0, 0],  # (B,C) vs (A) - INVALID: A appears twice
        ])
        # Fix again: proper valid match with 4 players
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 1, 1, 0],  # (A,D) vs (B,C)
            [0, 1, 0, 1, 1, 0, 0, 1],  # (B,D) vs (A,D) - INVALID: D appears twice!
        ])
        # Final fix: (B,D) vs (A,C)
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 1, 1, 0],  # (A,D) vs (B,C)
            [0, 1, 0, 1, 1, 0, 1, 0],  # (B,D) vs (A,C)
        ])
        calendar = Calendar(matches=matches, n_players=4)
        assert len(calendar) == 3
    
    def test_get_match(self):
        """Test get_match method returns Match object."""
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 1, 1, 0],  # (A,D) vs (B,C)
        ])
        calendar = Calendar(matches=matches, n_players=4)
        match = calendar.get_match(0)
        assert isinstance(match, Match)
        assert np.array_equal(match.match_vector, matches[0])
    
    def test_get_match_out_of_bounds(self):
        """Test get_match with invalid index."""
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        with pytest.raises(IndexError):
            calendar.get_match(5)
    
    def test_is_valid_method(self):
        """Test is_valid method returns True for valid calendar."""
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 1, 1, 0],  # (A,D) vs (B,C)
        ])
        calendar = Calendar(matches=matches, n_players=4)
        assert calendar.is_valid() is True
    
    def test_get_matches_per_player(self):
        """Test get_matches_per_player returns correct counts."""
        # 3 matches with 7 players
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],  # (A,D) vs (B,E)
            [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],  # (C,E) vs (C,F) - wait invalid
        ])
        # Fix: (C,E) vs (D,F)
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],  # (A,B) vs (C,D)
            [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],  # (A,D) vs (B,E)
            [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],  # (C,E) vs (D,F)
        ])
        calendar = Calendar(matches=matches, n_players=7)
        matches_per_player = calendar.get_matches_per_player()
        
        # A: match 0, 1 = 2
        # B: match 0, 1 = 2
        # C: match 0, 2 = 2
        # D: match 0, 1, 2 = 3
        # E: match 1, 2 = 2
        # F: match 2 = 1
        # G: match none = 0
        
        assert matches_per_player[0] == 2  # A
        assert matches_per_player[1] == 2  # B
        assert matches_per_player[2] == 2  # C
        assert matches_per_player[3] == 3  # D
        assert matches_per_player[4] == 2  # E
        assert matches_per_player[5] == 1  # F
        assert matches_per_player[6] == 0  # G
    
    def test_get_waiting_rounds_per_player(self):
        """Test get_waiting_rounds_per_player calculates gaps correctly."""
        # Player A plays matches 0, 3 -> waits 2 rounds (matches 1, 2)
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],  # Match 0: (A,B) vs (C,D)
            [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],  # Match 1: (C,D) vs (B,E)
            [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],  # Match 2: (C,E) vs (D,F)
            [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],  # Match 3: (A,D) vs (B,F)
        ])
        calendar = Calendar(matches=matches, n_players=7)
        waiting_rounds = calendar.get_waiting_rounds_per_player()
        
        # Player A (0): plays match 0, 3 -> gap = 2
        assert 2 in waiting_rounds[0]
        
        # Player B (1): plays match 0, 1, 3 -> gaps = [0, 1]
        assert waiting_rounds[1] == [0, 1]
    
    def test_empty_calendar(self):
        """Test calendar with no matches."""
        matches = np.array([]).reshape(0, 8)  # 0 matches, 8 columns (4 players)
        calendar = Calendar(matches=matches, n_players=4)
        assert len(calendar) == 0
        matches_per_player = calendar.get_matches_per_player()
        # All players should have 0 matches
        for count in matches_per_player.values():
            assert count == 0
    
    def test_single_match_calendar(self):
        """Test calendar with single match."""
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        assert len(calendar) == 1
        assert calendar.is_valid() is True
    
    def test_large_calendar_50_matches(self):
        """Test creating a large calendar with 50 matches."""
        matches = np.array([generate_random_match(7) for _ in range(50)])
        calendar = Calendar(matches=matches, n_players=7)
        assert len(calendar) == 50
        assert calendar.is_valid() is True

