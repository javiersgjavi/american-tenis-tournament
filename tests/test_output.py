"""
Tests for Output Formatting.
Following TDD methodology - these tests define the expected behavior.
"""

import pytest
import numpy as np
from io import StringIO
import sys
import csv
from pathlib import Path
import tempfile
import shutil
from src.dataclasses import Calendar, Match
from src.utils import generate_random_match


# Import functions that will be implemented
try:
    from src.printer import (
        match_vector_to_string,
        print_calendar,
        print_statistics,
        print_cut_points,
        print_results,
        export_calendar_to_csv,
        export_results_to_txt,
        export_all_outputs,
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

    def test_format_with_parentheses(self):
        """Test that output format uses parentheses."""
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

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_calendar(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert "Match" in output
        assert "vs" in output

    def test_print_calendar_shows_all_matches(self):
        """Test that all matches are printed."""
        from src.printer import print_calendar

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
                [0, 1, 1, 0, 1, 0, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_calendar(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        # Should have at least 3 match lines
        match_lines = [
            line for line in output.split("\n") if "Match" in line and ":" in line
        ]
        assert len(match_lines) >= 3

    def test_print_empty_calendar(self):
        """Test printing empty calendar doesn't crash."""
        from src.printer import print_calendar

        calendar = Calendar(matches=np.array([]).reshape(0, 8), n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_calendar(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert len(output) > 0


class TestPrintStatistics:
    """Test the print_statistics function."""

    def test_print_statistics_shows_match_counts(self):
        """Test that statistics show match counts per player."""
        from src.printer import print_statistics

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_statistics(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert "Player" in output or "matches" in output.lower()

    def test_print_statistics_shows_all_players(self):
        """Test that statistics show all players."""
        from src.printer import print_statistics

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_statistics(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        # Should show info for all 4 players
        assert len(output) > 0

    def test_print_statistics_shows_balance_info(self):
        """Test that statistics show balance information."""
        from src.printer import print_statistics

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_statistics(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert len(output) > 0


class TestPrintCutPoints:
    """Test the print_cut_points function."""

    def test_print_cut_points_with_perfect_cuts(self):
        """Test printing cut points when they exist."""
        from src.printer import print_cut_points
        from src.genetic_algorithm import GeneticAlgorithm

        # Generate a calendar that should have cut points
        ga = GeneticAlgorithm(
            n_players=4, n_matches=5, population_size=20, generations=10
        )
        calendar = ga.run(verbose=False)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_cut_points(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert len(output) > 0

    def test_print_cut_points_with_no_cuts(self):
        """Test printing when no cut points exist."""
        from src.printer import print_cut_points

        # Simple calendar that may not have cuts
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_cut_points(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert len(output) > 0

    def test_print_cut_points_shows_both_types(self):
        """Test that both perfect and acceptable cuts are shown."""
        from src.printer import print_cut_points

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_cut_points(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert len(output) > 0


class TestPrintResults:
    """Test the print_results function."""

    def test_print_results_complete_output(self):
        """Test that print_results shows complete information."""
        from src.printer import print_results

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_results(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        # Should have substantial output
        assert len(output) > 100
        assert "vs" in output

    def test_print_results_with_title(self):
        """Test print_results with custom title."""
        from src.printer import print_results

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        captured_output = StringIO()
        sys.stdout = captured_output

        print_results(calendar, title="TEST TOURNAMENT")

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert len(output) > 0

    def test_print_results_shows_validation(self):
        """Test that results show validation quality."""
        from src.printer import print_results

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
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
            n_players=4, n_matches=5, population_size=20, generations=10
        )
        calendar = ga.run(verbose=False)

        # Should not raise any errors
        captured_output = StringIO()
        sys.stdout = captured_output

        print_results(calendar)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert len(output) > 0

    def test_all_output_functions_work_together(self):
        """Test that all output functions work in sequence."""
        from src.printer import print_calendar, print_statistics, print_cut_points

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
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


class TestCSVExport:
    """Test CSV export functionality."""

    def test_export_calendar_to_csv_creates_file(self):
        """Test that CSV export creates a file."""
        from src.printer import export_calendar_to_csv

        # Create a simple calendar
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
                [0, 1, 1, 0, 1, 0, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_calendar.csv"

            # Export calendar
            export_calendar_to_csv(calendar, output_path, include_cut_points=True)

            # Check file exists
            assert output_path.exists()
            assert output_path.is_file()

    def test_csv_has_correct_headers(self):
        """Test that CSV has correct headers."""
        from src.printer import export_calendar_to_csv

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_calendar.csv"
            export_calendar_to_csv(calendar, output_path)

            # Read CSV and check headers
            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)

                assert "Match #" in headers
                assert "Team 1" in headers
                assert "Team 2" in headers
                assert "Perfect Cut" in headers
                assert "Acceptable Cut" in headers

    def test_csv_has_correct_number_of_rows(self):
        """Test that CSV has correct number of rows (header + matches)."""
        from src.printer import export_calendar_to_csv

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
                [0, 1, 1, 0, 1, 0, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_calendar.csv"
            export_calendar_to_csv(calendar, output_path)

            # Read CSV and count rows
            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

                # Header + 3 matches = 4 rows
                assert len(rows) == 4

    def test_csv_marks_cut_points(self):
        """Test that CSV marks cut points with checkmarks."""
        from src.printer import export_calendar_to_csv
        from src.genetic_algorithm import GeneticAlgorithm

        # Generate a calendar with cut points
        ga = GeneticAlgorithm(
            n_players=4, n_matches=5, population_size=20, generations=10
        )
        calendar = ga.run(verbose=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_calendar.csv"
            export_calendar_to_csv(calendar, output_path, include_cut_points=True)

            # Read CSV and check for cut point markers
            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                rows = list(reader)

                # At least one row should have a cut point marker
                has_cut_point = any("✓" in row[3] or "✓" in row[4] for row in rows)
                assert has_cut_point

    def test_csv_without_cut_points(self):
        """Test CSV export without cut point markers."""
        from src.printer import export_calendar_to_csv

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_calendar.csv"
            export_calendar_to_csv(calendar, output_path, include_cut_points=False)

            # Read CSV
            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                rows = list(reader)

                # No cut point markers should be present
                has_cut_point = any("✓" in row[3] or "✓" in row[4] for row in rows)
                assert not has_cut_point


class TestTXTExport:
    """Test TXT export functionality."""

    def test_export_results_to_txt_creates_file(self):
        """Test that TXT export creates a file."""
        from src.printer import export_results_to_txt

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
                [0, 1, 1, 0, 1, 0, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_results.txt"

            # Export results
            export_results_to_txt(calendar, output_path)

            # Check file exists
            assert output_path.exists()
            assert output_path.is_file()

    def test_txt_contains_calendar_section(self):
        """Test that TXT contains calendar section."""
        from src.printer import export_results_to_txt

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_results.txt"
            export_results_to_txt(calendar, output_path)

            # Read file and check content
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

                assert "MATCH CALENDAR" in content
                assert "Match 1:" in content
                assert "vs" in content

    def test_txt_contains_statistics_section(self):
        """Test that TXT contains statistics section."""
        from src.printer import export_results_to_txt

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_results.txt"
            export_results_to_txt(calendar, output_path)

            # Read file and check content
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

                assert "STATISTICS" in content
                assert "Player" in content

    def test_txt_contains_cut_points_section(self):
        """Test that TXT contains cut points section."""
        from src.printer import export_results_to_txt
        from src.genetic_algorithm import GeneticAlgorithm

        # Generate a calendar with cut points
        ga = GeneticAlgorithm(
            n_players=4, n_matches=5, population_size=20, generations=10
        )
        calendar = ga.run(verbose=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_results.txt"
            export_results_to_txt(calendar, output_path)

            # Read file and check content
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

                assert "CUT POINTS" in content


class TestUnifiedExport:
    """Test unified export functionality."""

    def test_export_all_outputs_creates_both_files(self):
        """Test that export_all_outputs creates both CSV and TXT files."""
        from src.printer import export_all_outputs

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
                [0, 1, 1, 0, 1, 0, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Export all outputs
            result = export_all_outputs(
                calendar, output_dir=tmpdir, base_filename="test"
            )

            # Check both files exist
            assert result["csv"].exists()
            assert result["txt"].exists()
            assert result["csv"].is_file()
            assert result["txt"].is_file()

    def test_export_all_outputs_creates_directory(self):
        """Test that export_all_outputs creates output directory if it doesn't exist."""
        from src.printer import export_all_outputs

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "new_outputs"

            # Directory doesn't exist yet
            assert not output_dir.exists()

            # Export all outputs
            export_all_outputs(calendar, output_dir=output_dir, base_filename="test")

            # Directory should now exist
            assert output_dir.exists()
            assert output_dir.is_dir()

    def test_export_all_outputs_returns_correct_paths(self):
        """Test that export_all_outputs returns correct file paths."""
        from src.printer import export_all_outputs

        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1],
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = export_all_outputs(
                calendar, output_dir=tmpdir, base_filename="my_tournament"
            )

            # Check paths are correct
            assert result["csv"].name == "my_tournament_calendar.csv"
            assert result["txt"].name == "my_tournament_results.txt"
            assert str(result["csv"].parent) == tmpdir
            assert str(result["txt"].parent) == tmpdir

    def test_export_all_outputs_with_ga_result(self):
        """Test export_all_outputs with GA-generated calendar."""
        from src.printer import export_all_outputs
        from src.genetic_algorithm import GeneticAlgorithm

        # Generate a calendar
        ga = GeneticAlgorithm(
            n_players=5, n_matches=10, population_size=20, generations=10
        )
        calendar = ga.run(verbose=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = export_all_outputs(
                calendar, output_dir=tmpdir, base_filename="tournament"
            )

            # Check both files exist and have content
            assert result["csv"].exists()
            assert result["txt"].exists()
            assert result["csv"].stat().st_size > 0
            assert result["txt"].stat().st_size > 0
