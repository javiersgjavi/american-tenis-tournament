"""
Tests for Match class and match-related functions.
Following TDD methodology - these tests define the expected behavior.
"""

import pytest
import numpy as np
from src.genetic_algorithm import Match, generate_random_match, is_valid_match


class TestIsValidMatch:
    """Test the is_valid_match function."""

    def test_valid_match_4_players(self):
        """Test a valid match with 4 players."""
        # Match: (A,B) vs (C,D) with 4 players
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 1])
        assert is_valid_match(match_vector) is True

    def test_valid_match_7_players(self):
        """Test a valid match with 7 players."""
        # Match: (A,D) vs (B,C) with 7 players
        match_vector = np.array([1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0])
        assert is_valid_match(match_vector) is True

    def test_invalid_match_too_few_players(self):
        """Test invalid match with less than 4 players."""
        # Only 3 players
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 0])
        assert is_valid_match(match_vector) is False

    def test_invalid_match_too_many_players(self):
        """Test invalid match with more than 4 players."""
        # 5 players
        match_vector = np.array([1, 1, 1, 0, 0, 0, 1, 1])
        assert is_valid_match(match_vector) is False

    def test_invalid_match_unbalanced_teams(self):
        """Test invalid match with unbalanced teams."""
        # Team 1 has 3 players, team 2 has 1
        match_vector = np.array([1, 1, 1, 0, 0, 0, 0, 1])
        assert is_valid_match(match_vector) is False

    def test_invalid_match_player_in_both_teams(self):
        """Test invalid match with player in both teams."""
        # Player A (index 0) in both teams
        match_vector = np.array([1, 1, 0, 0, 1, 0, 1, 0])
        assert is_valid_match(match_vector) is False

    def test_invalid_match_empty_teams(self):
        """Test invalid match with empty teams."""
        match_vector = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        assert is_valid_match(match_vector) is False


class TestGenerateRandomMatch:
    """Test the generate_random_match function."""

    def test_generates_valid_match_4_players(self):
        """Test that generated match is valid for 4 players."""
        match_vector = generate_random_match(4)
        assert is_valid_match(match_vector) is True

    def test_generates_valid_match_7_players(self):
        """Test that generated match is valid for 7 players."""
        match_vector = generate_random_match(7)
        assert is_valid_match(match_vector) is True

    def test_generates_valid_match_10_players(self):
        """Test that generated match is valid for 10 players."""
        match_vector = generate_random_match(10)
        assert is_valid_match(match_vector) is True

    def test_correct_vector_length(self):
        """Test that generated match has correct length."""
        n_players = 7
        match_vector = generate_random_match(n_players)
        assert len(match_vector) == 2 * n_players

    def test_generates_different_matches(self):
        """Test that function generates different matches (randomness)."""
        matches = [generate_random_match(7) for _ in range(10)]
        # At least some matches should be different
        unique_matches = {tuple(m) for m in matches}
        assert len(unique_matches) > 1


class TestMatch:
    """Test the Match class."""

    def test_create_valid_match(self):
        """Test creating a valid Match instance."""
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 1])
        match = Match(match_vector=match_vector, n_players=4)
        assert match is not None

    def test_create_invalid_match_raises_error(self):
        """Test that creating invalid Match raises ValidationError."""
        from pydantic import ValidationError

        invalid_vector = np.array([1, 1, 1, 0, 0, 0, 1, 0])  # Invalid: 3 vs 1
        with pytest.raises(ValidationError):
            Match(match_vector=invalid_vector, n_players=4)

    def test_is_valid_method(self):
        """Test the is_valid method."""
        match_vector = np.array([1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0])
        match = Match(match_vector=match_vector, n_players=7)
        assert match.is_valid() is True

    def test_get_players(self):
        """Test get_players method returns correct player indices."""
        # Match: (A,B) vs (C,D) = players 0,1,2,3
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 1])
        match = Match(match_vector=match_vector, n_players=4)
        players = match.get_players()
        assert set(players) == {0, 1, 2, 3}
        assert len(players) == 4

    def test_get_teams(self):
        """Test get_teams method returns correct teams."""
        # Match: (A,D) vs (B,C) with 7 players
        match_vector = np.array([1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0])
        match = Match(match_vector=match_vector, n_players=7)
        team1, team2 = match.get_teams()
        assert set(team1) == {0, 3}  # A, D
        assert set(team2) == {1, 2}  # B, C
        assert len(team1) == 2
        assert len(team2) == 2

    def test_str_representation(self):
        """Test string representation of match."""
        # Match: (A,B) vs (C,D)
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 1])
        match = Match(match_vector=match_vector, n_players=4)
        match_str = str(match)
        # Should contain team format
        assert "vs" in match_str
        assert "(" in match_str and ")" in match_str

    def test_match_with_7_players_scenario(self):
        """Test realistic scenario with 7 players."""
        # Match: (E,F) vs (A,G) = (4,5) vs (0,6)
        match_vector = np.array([0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1])
        match = Match(match_vector=match_vector, n_players=7)
        team1, team2 = match.get_teams()
        assert set(team1) == {4, 5}
        assert set(team2) == {0, 6}
