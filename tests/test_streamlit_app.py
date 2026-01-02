"""
Tests for the Streamlit web application helper functions.

These tests verify the utility functions used in the Streamlit app
without requiring a running Streamlit server.
"""

import pytest
import numpy as np
from src.dataclasses import Match, Calendar
from src.genetic_algorithm import GeneticAlgorithm


# =============================================================================
# IMPORT APP FUNCTIONS
# =============================================================================

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_app import get_player_name, calendar_to_csv, replace_letters_with_names


# =============================================================================
# TEST GET_PLAYER_NAME FUNCTION
# =============================================================================

class TestGetPlayerName:
    """Tests for the get_player_name function."""
    
    def test_first_player_is_a(self):
        """Test that player index 0 returns 'A' with no custom names."""
        assert get_player_name(0) == "A"
    
    def test_second_player_is_b(self):
        """Test that player index 1 returns 'B' with no custom names."""
        assert get_player_name(1) == "B"
    
    def test_player_indices_0_to_7(self):
        """Test player indices 0-7 return A-H with no custom names."""
        expected = ["A", "B", "C", "D", "E", "F", "G", "H"]
        for i, letter in enumerate(expected):
            assert get_player_name(i) == letter
    
    def test_player_index_25_is_z(self):
        """Test that player index 25 returns 'Z'."""
        assert get_player_name(25) == "Z"
    
    def test_all_letters_unique(self):
        """Test that all player names from 0-25 are unique."""
        names = [get_player_name(i) for i in range(26)]
        assert len(names) == len(set(names))
    
    def test_custom_name_overrides_letter(self):
        """Test that custom names override default letters."""
        custom_names = ["Juan", "María", "Pedro", "Ana"]
        assert get_player_name(0, custom_names) == "Juan"
        assert get_player_name(1, custom_names) == "María"
        assert get_player_name(2, custom_names) == "Pedro"
        assert get_player_name(3, custom_names) == "Ana"
    
    def test_empty_custom_name_uses_letter(self):
        """Test that empty custom names fall back to letters."""
        custom_names = ["Juan", "", "Pedro", ""]
        assert get_player_name(0, custom_names) == "Juan"
        assert get_player_name(1, custom_names) == "B"  # Empty, use letter
        assert get_player_name(2, custom_names) == "Pedro"
        assert get_player_name(3, custom_names) == "D"  # Empty, use letter
    
    def test_whitespace_custom_name_uses_letter(self):
        """Test that whitespace-only custom names fall back to letters."""
        custom_names = ["Juan", "   ", "Pedro"]
        assert get_player_name(0, custom_names) == "Juan"
        assert get_player_name(1, custom_names) == "B"  # Whitespace, use letter


# =============================================================================
# TEST REPLACE_LETTERS_WITH_NAMES FUNCTION
# =============================================================================

class TestReplaceLettersWithNames:
    """Tests for the replace_letters_with_names function."""
    
    def test_no_replacement_without_custom_names(self):
        """Test that text is unchanged without custom names."""
        text = "(A,B) vs (C,D)"
        result = replace_letters_with_names(text, 4, None)
        assert result == "(A,B) vs (C,D)"
    
    def test_replaces_all_letters(self):
        """Test that all letters are replaced with custom names."""
        text = "(A,B) vs (C,D)"
        custom_names = ["Juan", "María", "Pedro", "Ana"]
        result = replace_letters_with_names(text, 4, custom_names)
        assert result == "(Juan,María) vs (Pedro,Ana)"
    
    def test_partial_replacement(self):
        """Test that only provided names are replaced."""
        text = "(A,B) vs (C,D)"
        custom_names = ["Juan", "", "Pedro", ""]  # Only A and C have names
        result = replace_letters_with_names(text, 4, custom_names)
        assert result == "(Juan,B) vs (Pedro,D)"


# =============================================================================
# TEST CALENDAR_TO_CSV FUNCTION
# =============================================================================

class TestCalendarToCsv:
    """Tests for the calendar_to_csv function."""
    
    @pytest.fixture
    def simple_calendar(self):
        """Create a simple calendar with 4 players and 2 matches."""
        n_players = 4
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 1, 0, 0, 1, 0, 1],  # (A,C) vs (B,D)
        ])
        return Calendar(matches=matches, n_players=n_players, n_courts=1)
    
    @pytest.fixture
    def multi_court_calendar(self):
        """Create a calendar with 8 players and 2 courts."""
        n_players = 8
        matches = np.array([
            # Round 1 - Court 1: (A,B) vs (C,D)
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            # Round 1 - Court 2: (E,F) vs (G,H)
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            # Round 2 - Court 1: (A,E) vs (B,F)
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            # Round 2 - Court 2: (C,G) vs (D,H)
            [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        ])
        return Calendar(matches=matches, n_players=n_players, n_courts=2)
    
    def test_csv_has_header(self, simple_calendar):
        """Test that CSV output has the expected header."""
        csv = calendar_to_csv(simple_calendar)
        lines = csv.split("\n")
        assert lines[0] == "Round,Court,Match,Team 1,Team 2,Perfect Cut,Acceptable Cut"
    
    def test_csv_has_correct_number_of_lines(self, simple_calendar):
        """Test that CSV has header + one line per match."""
        csv = calendar_to_csv(simple_calendar)
        lines = csv.split("\n")
        # Header + 2 matches
        assert len(lines) == 3
    
    def test_csv_match_format(self, simple_calendar):
        """Test that match lines have correct format."""
        csv = calendar_to_csv(simple_calendar)
        lines = csv.split("\n")
        # First match line (skip header)
        parts = lines[1].split(",")
        # Should have: Round, Court, Match#, Team1, Team2, Perfect, Acceptable
        assert len(parts) >= 7
    
    def test_csv_multi_court_rounds(self, multi_court_calendar):
        """Test that multi-court calendar shows correct rounds."""
        csv = calendar_to_csv(multi_court_calendar)
        lines = csv.split("\n")
        
        # Line 1: Round 1, Court 1
        assert lines[1].startswith("1,1,1,")
        # Line 2: Round 1, Court 2
        assert lines[2].startswith("1,2,2,")
        # Line 3: Round 2, Court 1
        assert lines[3].startswith("2,1,3,")
        # Line 4: Round 2, Court 2
        assert lines[4].startswith("2,2,4,")
    
    def test_csv_returns_string(self, simple_calendar):
        """Test that calendar_to_csv returns a string."""
        csv = calendar_to_csv(simple_calendar)
        assert isinstance(csv, str)
    
    def test_csv_not_empty(self, simple_calendar):
        """Test that CSV output is not empty."""
        csv = calendar_to_csv(simple_calendar)
        assert len(csv) > 0
    
    def test_csv_with_custom_names(self, simple_calendar):
        """Test that CSV uses custom names when provided."""
        custom_names = ["Juan", "María", "Pedro", "Ana"]
        csv = calendar_to_csv(simple_calendar, custom_names)
        assert "Juan" in csv
        assert "María" in csv
        assert "Pedro" in csv
        assert "Ana" in csv


# =============================================================================
# TEST STREAMLIT APP INTEGRATION
# =============================================================================

class TestStreamlitAppIntegration:
    """Integration tests for the Streamlit app workflow."""
    
    def test_ga_generates_valid_calendar(self):
        """Test that GA generates a calendar usable by the app."""
        ga = GeneticAlgorithm(
            n_players=8,
            n_rounds=5,
            n_courts=2,
            population_size=50,
            generations=50,
            mutation_rate=0.2,
            crossover_rate=0.8,
            elitism_size=2,
            n_jobs=1,
            early_stopping_patience=20,
        )
        
        calendar = ga.run(verbose=False)
        
        assert calendar is not None
        assert len(calendar) == 10  # 5 rounds * 2 courts
        assert calendar.n_players == 8
        assert calendar.n_courts == 2
    
    def test_ga_with_progress_callback(self):
        """Test that GA works with progress callback."""
        ga = GeneticAlgorithm(
            n_players=8,
            n_rounds=3,
            n_courts=2,
            population_size=30,
            generations=30,
            mutation_rate=0.2,
            crossover_rate=0.8,
            elitism_size=2,
            n_jobs=1,
            early_stopping_patience=10,
        )
        
        callback_calls = []
        
        def test_callback(gen, total_gen, best_fit, avg_fit):
            callback_calls.append((gen, total_gen, best_fit, avg_fit))
            return True  # Continue
        
        calendar = ga.run(verbose=False, progress_callback=test_callback)
        
        assert calendar is not None
        assert len(callback_calls) > 0
        # First call should be generation 1
        assert callback_calls[0][0] == 1
    
    def test_generated_calendar_can_be_converted_to_csv(self):
        """Test that a generated calendar can be converted to CSV."""
        ga = GeneticAlgorithm(
            n_players=8,
            n_rounds=3,
            n_courts=2,
            population_size=30,
            generations=30,
            mutation_rate=0.2,
            crossover_rate=0.8,
            elitism_size=2,
            n_jobs=1,
            early_stopping_patience=10,
        )
        
        calendar = ga.run(verbose=False)
        csv = calendar_to_csv(calendar)
        
        assert isinstance(csv, str)
        lines = csv.split("\n")
        assert len(lines) == 7  # Header + 6 matches (3 rounds * 2 courts)
    
    def test_csv_contains_all_matches(self):
        """Test that CSV contains all matches from calendar."""
        ga = GeneticAlgorithm(
            n_players=8,
            n_rounds=4,
            n_courts=1,
            population_size=30,
            generations=30,
            mutation_rate=0.2,
            crossover_rate=0.8,
            elitism_size=2,
            n_jobs=1,
            early_stopping_patience=10,
        )
        
        calendar = ga.run(verbose=False)
        csv = calendar_to_csv(calendar)
        
        lines = csv.split("\n")
        # Header + 4 matches
        assert len(lines) == 5


# =============================================================================
# TEST EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_minimum_players(self):
        """Test with minimum number of players (4)."""
        n_players = 4
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
        ])
        calendar = Calendar(matches=matches, n_players=n_players, n_courts=1)
        
        csv = calendar_to_csv(calendar)
        assert "A & B" in csv or "B & A" in csv
    
    def test_large_player_count(self):
        """Test player name generation for large player counts."""
        # Test up to player index 15 (should be 'P')
        assert get_player_name(15) == "P"
    
    def test_csv_encoding_safe(self):
        """Test that CSV output is UTF-8 safe."""
        n_players = 4
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=n_players, n_courts=1)
        
        csv = calendar_to_csv(calendar)
        # Should be encodable to UTF-8 without errors
        csv.encode('utf-8')
    
    def test_csv_with_special_characters_in_names(self):
        """Test that CSV handles special characters in names."""
        n_players = 4
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=n_players, n_courts=1)
        
        custom_names = ["José", "María", "Señor", "Niño"]
        csv = calendar_to_csv(calendar, custom_names)
        
        assert "José" in csv
        assert "María" in csv
        csv.encode('utf-8')  # Should not raise
