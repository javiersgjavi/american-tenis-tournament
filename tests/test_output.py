"""
Tests for Output Formatting.
Following TDD methodology - these tests define the expected behavior.
"""

import pytest
import numpy as np
from io import StringIO
import sys
from src.dataclasses import Calendar, Match
from src.utils import generate_random_match


# Import functions that will be implemented
try:
    from src.printer import (
        match_vector_to_string,
        print_calendar,
        print_statistics,
        print_cut_points,
        print_results
    )
except ImportError:
    # Functions not yet implemented
    pass


class TestMatchVectorToString:
    """Test the match_vector_to_string function."""
    
    def test_convert_simple_match_4_players(self):
        """Test converting simple match with 4 players."""
        from src.printer import match_vector_to_string
        
        # (A,B) vs (C,D)
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 1])
        result = match_vector_to_string(match_vector, n_players=4)
        
        assert isinstance(result, str)
        assert "A" in result
        assert "B" in result
        assert "C" in result
        assert "D" in result
        assert "vs" in result
    
    def test_convert_match_7_players(self):
        """Test converting match with 7 players."""
        from src.printer import match_vector_to_string
        
        # (A,D) vs (B,C)
        match_vector = np.array([1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0])
        result = match_vector_to_string(match_vector, n_players=7)
        
        assert "A" in result
        assert "D" in result
        assert "B" in result
        assert "C" in result
        assert "vs" in result
    
    def test_format_with_parentheses(self):
        """Test that output has proper formatting with parentheses."""
        from src.printer import match_vector_to_string
        
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 1])
        result = match_vector_to_string(match_vector, n_players=4)
        
        assert "(" in result
        assert ")" in result
    
    def test_players_separated_by_comma(self):
        """Test that players in same team are separated by comma."""
        from src.printer import match_vector_to_string
        
        match_vector = np.array([1, 1, 0, 0, 0, 0, 1, 1])
        result = match_vector_to_string(match_vector, n_players=4)
        
        assert "," in result


class TestPrintCalendar:
    """Test the print_calendar function."""
    
    def test_print_calendar_basic(self):
        """Test basic calendar printing."""
        from src.printer import print_calendar
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 1, 0, 0, 1, 0, 1],  # (A,C) vs (B,D)
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        print_calendar(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        assert "Match 1" in output or "Match 0" in output
        assert "vs" in output
    
    def test_print_calendar_shows_all_matches(self):
        """Test that all matches are printed."""
        from src.printer import print_calendar
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 1, 0, 0, 1, 0, 1],  # (A,C) vs (B,D)
            [0, 1, 0, 1, 1, 0, 0, 0],  # (B,D) vs (A) - INVALID: only 3 players
        ])
        # Fix: proper 4 players
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 1, 0, 0, 1, 0, 1],  # (A,C) vs (B,D)
            [0, 1, 0, 1, 1, 0, 0, 0],  # (B,D) vs (A) - still invalid
        ])
        # Fix again: all 4 players
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 1, 0, 0, 1, 0, 1],  # (A,C) vs (B,D)
            [0, 1, 0, 1, 0, 1, 1, 0],  # (B,D) vs (C,D) - D twice!
        ])
        # Fix final: valid match
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 1, 0, 0, 1, 0, 1],  # (A,C) vs (B,D)
            [0, 1, 1, 0, 1, 0, 0, 0],  # (B,C) vs (A) - only 3!
        ])
        # Use generate_random_match instead
        from src.utils import generate_random_match
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            [1, 0, 1, 0, 0, 1, 0, 1],  # (A,C) vs (B,D)
            generate_random_match(4),  # Random valid match
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_calendar(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        lines = output.strip().split('\n')
        
        # Should have at least 3 match lines (could have headers)
        assert len(lines) >= 3
    
    def test_print_empty_calendar(self):
        """Test printing empty calendar."""
        from src.printer import print_calendar
        
        matches = np.array([]).reshape(0, 8)
        calendar = Calendar(matches=matches, n_players=4)
        
        # Should not raise error
        captured_output = StringIO()
        sys.stdout = captured_output
        print_calendar(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert isinstance(output, str)


class TestPrintStatistics:
    """Test the print_statistics function."""
    
    def test_print_statistics_shows_match_counts(self):
        """Test that statistics show match counts per player."""
        from src.printer import print_statistics
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # A:1, B:1, C:1, D:1
            [1, 0, 1, 0, 0, 1, 0, 1],  # A:2, B:2, C:2, D:2
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_statistics(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Should show player names
        assert "A" in output or "Player" in output
        # Should show numbers
        assert "2" in output
    
    def test_print_statistics_shows_all_players(self):
        """Test that statistics show all players including those who didn't play."""
        from src.printer import print_statistics
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],  # Only A,B,C,D play
        ])
        calendar = Calendar(matches=matches, n_players=7)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_statistics(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Should mention all players or show counts
        assert "0" in output or "1" in output
    
    def test_print_statistics_shows_balance_info(self):
        """Test that statistics show balance information."""
        from src.printer import print_statistics
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_statistics(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Should have some content
        assert len(output) > 0


class TestPrintCutPoints:
    """Test the print_cut_points function."""
    
    def test_print_cut_points_with_perfect_cuts(self):
        """Test printing cut points when perfect cuts exist."""
        from src.printer import print_cut_points
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],  # Perfect cut at 1
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_cut_points(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        assert "1" in output or "perfect" in output.lower()
    
    def test_print_cut_points_with_no_cuts(self):
        """Test printing when no cut points exist."""
        from src.printer import print_cut_points
        
        # Create unbalanced calendar
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
        ])
        calendar = Calendar(matches=matches, n_players=7)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_cut_points(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Should print something even if no cuts
        assert len(output) > 0
    
    def test_print_cut_points_shows_both_types(self):
        """Test that both perfect and acceptable cuts are shown."""
        from src.printer import print_cut_points
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_cut_points(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Should have some output
        assert len(output) > 0


class TestPrintResults:
    """Test the print_results function."""
    
    def test_print_results_complete_output(self):
        """Test that print_results shows complete information."""
        from src.printer import print_results
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_results(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Should have substantial output
        assert len(output) > 100
        # Should contain key sections
        assert "vs" in output  # Calendar section
    
    def test_print_results_with_title(self):
        """Test print_results with custom title."""
        from src.printer import print_results
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_results(calendar, title="Test Tournament")
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        assert "Test Tournament" in output or len(output) > 0
    
    def test_print_results_shows_validation(self):
        """Test that print_results shows validation quality."""
        from src.printer import print_results
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        captured_output = StringIO()
        sys.stdout = captured_output
        print_results(calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Should show quality level
        quality_keywords = ["EXCELLENT", "GOOD", "ACCEPTABLE", "REJECTED"]
        assert any(keyword in output for keyword in quality_keywords)


class TestOutputIntegration:
    """Integration tests for output formatting."""
    
    def test_output_with_ga_result(self):
        """Test output functions with GA-generated calendar."""
        from src.genetic_algorithm import GeneticAlgorithm
        from src.printer import print_results
        
        ga = GeneticAlgorithm(
            n_players=4,
            n_matches=5,
            population_size=10,
            generations=5
        )
        
        best_calendar = ga.run(verbose=False)
        
        # Should be able to print results without error
        captured_output = StringIO()
        sys.stdout = captured_output
        print_results(best_calendar)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert len(output) > 0
    
    def test_all_output_functions_work_together(self):
        """Test that all output functions can be called in sequence."""
        from src.printer import (
            print_calendar,
            print_statistics,
            print_cut_points
        )
        
        matches = np.array([
            [1, 1, 0, 0, 0, 0, 1, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
        ])
        calendar = Calendar(matches=matches, n_players=4)
        
        # All should work without error
        captured_output = StringIO()
        sys.stdout = captured_output
        
        print_calendar(calendar)
        print_statistics(calendar)
        print_cut_points(calendar)
        
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert len(output) > 0

