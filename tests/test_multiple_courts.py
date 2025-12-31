"""
Tests for multiple courts functionality (n_courts, rounds).
These tests verify the new round-based features work correctly.
"""

import pytest
import numpy as np
from src.dataclasses import (
    Calendar,
    Match,
    get_minimum_players_for_courts,
    can_use_multiple_courts,
)
from src.genetic_algorithm import (
    GeneticAlgorithm,
    calculate_round_conflict_penalty,
    calculate_waiting_penalty,
    calculate_early_cut_bonus,
    calculate_fitness,
    detect_cut_points,
    validate_solution,
)
from src.utils import generate_random_match


class TestMultipleCourtsHelpers:
    """Test helper functions for multiple courts."""

    def test_minimum_players_for_1_court(self):
        """Test minimum players for 1 court is 4."""
        assert get_minimum_players_for_courts(1) == 4

    def test_minimum_players_for_2_courts(self):
        """Test minimum players for 2 courts is 8."""
        assert get_minimum_players_for_courts(2) == 8

    def test_minimum_players_for_3_courts(self):
        """Test minimum players for 3 courts is 12."""
        assert get_minimum_players_for_courts(3) == 12

    def test_can_use_multiple_courts_valid(self):
        """Test that 8 players can use 2 courts."""
        assert can_use_multiple_courts(8, 2) is True

    def test_can_use_multiple_courts_invalid(self):
        """Test that 6 players cannot use 2 courts."""
        assert can_use_multiple_courts(6, 2) is False

    def test_can_use_single_court_with_4_players(self):
        """Test that 4 players can use 1 court."""
        assert can_use_multiple_courts(4, 1) is True


class TestCalendarWithCourts:
    """Test Calendar class with n_courts parameter."""

    def test_create_calendar_with_1_court_default(self):
        """Test that default n_courts is 1."""
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 1, 1],  # (A,B) vs (C,D)
            ]
        )
        calendar = Calendar(matches=matches, n_players=4)
        assert calendar.n_courts == 1

    def test_create_calendar_with_2_courts(self):
        """Test creating calendar with 2 courts."""
        # For 8 players: vector is [team1(8 positions), team2(8 positions)]
        # (A,B) vs (C,D): team1=[1,1,0,0,0,0,0,0], team2=[0,0,1,1,0,0,0,0]
        # (E,F) vs (G,H): team1=[0,0,0,0,1,1,0,0], team2=[0,0,0,0,0,0,1,1]
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # (A,B) vs (C,D)
                [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # (E,F) vs (G,H)
            ]
        )
        calendar = Calendar(matches=matches, n_players=8, n_courts=2)
        assert calendar.n_courts == 2

    def test_get_total_rounds_single_court(self):
        """Test get_total_rounds with 1 court."""
        matches = np.array([generate_random_match(4) for _ in range(5)])
        calendar = Calendar(matches=matches, n_players=4, n_courts=1)
        assert calendar.get_total_rounds() == 5

    def test_get_total_rounds_two_courts(self):
        """Test get_total_rounds with 2 courts."""
        matches = np.array([generate_random_match(8) for _ in range(6)])
        calendar = Calendar(matches=matches, n_players=8, n_courts=2)
        assert calendar.get_total_rounds() == 3  # 6 matches / 2 courts = 3 rounds

    def test_get_round_for_match_single_court(self):
        """Test get_round_for_match with 1 court."""
        matches = np.array([generate_random_match(4) for _ in range(3)])
        calendar = Calendar(matches=matches, n_players=4, n_courts=1)
        assert calendar.get_round_for_match(0) == 1
        assert calendar.get_round_for_match(1) == 2
        assert calendar.get_round_for_match(2) == 3

    def test_get_round_for_match_two_courts(self):
        """Test get_round_for_match with 2 courts."""
        matches = np.array([generate_random_match(8) for _ in range(4)])
        calendar = Calendar(matches=matches, n_players=8, n_courts=2)
        assert calendar.get_round_for_match(0) == 1
        assert calendar.get_round_for_match(1) == 1  # Same round
        assert calendar.get_round_for_match(2) == 2
        assert calendar.get_round_for_match(3) == 2  # Same round

    def test_get_matches_in_round_single_court(self):
        """Test get_matches_in_round with 1 court."""
        matches = np.array([generate_random_match(4) for _ in range(3)])
        calendar = Calendar(matches=matches, n_players=4, n_courts=1)
        assert calendar.get_matches_in_round(1) == [0]
        assert calendar.get_matches_in_round(2) == [1]
        assert calendar.get_matches_in_round(3) == [2]

    def test_get_matches_in_round_two_courts(self):
        """Test get_matches_in_round with 2 courts."""
        matches = np.array([generate_random_match(8) for _ in range(4)])
        calendar = Calendar(matches=matches, n_players=8, n_courts=2)
        assert calendar.get_matches_in_round(1) == [0, 1]
        assert calendar.get_matches_in_round(2) == [2, 3]


class TestRoundConflicts:
    """Test round conflict detection."""

    def test_no_conflict_single_court(self):
        """Test no conflict with single court."""
        matches = np.array([generate_random_match(4) for _ in range(3)])
        calendar = Calendar(matches=matches, n_players=4, n_courts=1)
        assert calendar.has_round_conflicts() is False

    def test_no_conflict_different_players_per_round(self):
        """Test no conflict when different players in same round."""
        # Round 1: (A,B) vs (C,D) and (E,F) vs (G,H) - no overlap
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # (A,B) vs (C,D)
                [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # (E,F) vs (G,H)
            ]
        )
        calendar = Calendar(matches=matches, n_players=8, n_courts=2)
        assert calendar.has_round_conflicts() is False

    def test_conflict_same_player_in_round(self):
        """Test conflict when same player in two matches of same round."""
        # Round 1: Player A is in both matches
        # Use model_construct to bypass validation for testing conflict detection
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # (A,B) vs (C,D)
                [
                    1,
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    1,
                ],  # (A,E) vs (G,H) - A again!
            ]
        )
        calendar = Calendar.model_construct(matches=matches, n_players=8, n_courts=2)
        assert calendar.has_round_conflicts() is True

    def test_get_round_conflicts_details(self):
        """Test getting detailed conflict information."""
        # Round 1: Player A (index 0) is in both matches
        # Use model_construct to bypass validation for testing conflict detection
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # (A,B) vs (C,D)
                [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # (A,E) vs (G,H)
            ]
        )
        calendar = Calendar.model_construct(matches=matches, n_players=8, n_courts=2)
        conflicts = calendar.get_round_conflicts()
        assert len(conflicts) == 1
        assert conflicts[0][0] == 1  # Round 1
        assert conflicts[0][1] == 0  # Player A (index 0)
        assert conflicts[0][2] == 2  # Appears 2 times


class TestRoundConflictPenalty:
    """Test calculate_round_conflict_penalty function."""

    def test_no_conflict_zero_penalty(self):
        """Test zero penalty when no conflicts."""
        matches = np.array([generate_random_match(8) for _ in range(4)])
        # Create valid calendar without conflicts
        calendar = Calendar(
            matches=matches, n_players=8, n_courts=1
        )  # Single court = no conflicts
        penalty = calculate_round_conflict_penalty(calendar)
        assert penalty == 0.0

    def test_conflict_infinite_penalty(self):
        """Test infinite penalty when conflict exists."""
        # Use model_construct to bypass validation for testing the penalty function
        # (A,B) vs (C,D) and (A,E) vs (G,H) - A is in both matches of round 1
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # (A,B) vs (C,D)
                [
                    1,
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    1,
                ],  # (A,E) vs (G,H) - A again!
            ]
        )
        calendar = Calendar.model_construct(matches=matches, n_players=8, n_courts=2)
        penalty = calculate_round_conflict_penalty(calendar)
        assert penalty == float("inf")


class TestWaitingPenaltyWithRounds:
    """Test waiting penalty with multiple courts."""

    def test_all_players_play_every_round_zero_waiting(self):
        """Test zero waiting when all players play every round."""
        # With 8 players and 2 courts, all 8 can play each round
        ga = GeneticAlgorithm(
            n_players=8, n_rounds=3, n_courts=2, population_size=5, generations=1
        )
        calendar = ga._generate_valid_calendar()

        # With 8 players and 2 courts (4 per match x 2 = 8), everyone plays every round
        penalty = calculate_waiting_penalty(calendar)
        assert penalty == 0.0


class TestCutPointsWithRounds:
    """Test cut points detection with multiple courts."""

    def test_cut_points_at_round_boundaries_only(self):
        """Test that cut points are only at round boundaries."""
        # Create a balanced calendar with 2 courts
        ga = GeneticAlgorithm(
            n_players=8, n_rounds=4, n_courts=2, population_size=10, generations=5
        )
        best_calendar = ga.run(verbose=False)

        perfect_cuts, acceptable_cuts = detect_cut_points(best_calendar)

        # Cut points should be round numbers (1, 2, 3, 4), not match indices
        for cut in perfect_cuts + acceptable_cuts:
            assert cut <= 4  # Max round number
            assert cut >= 1


class TestGeneticAlgorithmWithRounds:
    """Test GeneticAlgorithm with n_rounds parameter."""

    def test_create_ga_with_n_rounds(self):
        """Test creating GA with n_rounds parameter."""
        ga = GeneticAlgorithm(
            n_players=8, n_rounds=10, n_courts=2, population_size=5, generations=1
        )
        assert ga.n_rounds == 10
        assert ga.n_courts == 2
        assert ga.n_matches == 20  # 10 rounds * 2 courts

    def test_ga_validates_minimum_players(self):
        """Test that GA validates minimum players for courts."""
        with pytest.raises(ValueError, match="Not enough players"):
            GeneticAlgorithm(
                n_players=6,  # Need 8 for 2 courts
                n_rounds=5,
                n_courts=2,
                population_size=5,
                generations=1,
            )

    def test_ga_produces_valid_calendars_with_courts(self):
        """Test that GA produces valid calendars with multiple courts."""
        ga = GeneticAlgorithm(
            n_players=8, n_rounds=5, n_courts=2, population_size=10, generations=3
        )
        best_calendar = ga.run(verbose=False)

        assert best_calendar.is_valid()
        assert best_calendar.n_courts == 2
        assert len(best_calendar) == 10  # 5 rounds * 2 courts
        assert not best_calendar.has_round_conflicts()

    def test_ga_single_court_backward_compatible(self):
        """Test that GA with n_courts=1 is backward compatible."""
        ga = GeneticAlgorithm(
            n_players=4, n_rounds=5, n_courts=1, population_size=10, generations=3
        )
        best_calendar = ga.run(verbose=False)

        assert best_calendar.is_valid()
        assert best_calendar.n_courts == 1
        assert len(best_calendar) == 5  # 5 rounds * 1 court
        assert best_calendar.get_total_rounds() == 5


class TestValidateSolutionWithRounds:
    """Test validate_solution with multiple courts."""

    def test_validate_detects_round_conflicts(self):
        """Test that validation detects round conflicts."""
        # Use model_construct to bypass validation for testing validate_solution
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # (A,B) vs (C,D)
                [
                    1,
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    1,
                ],  # (A,E) vs (G,H) - A again!
            ]
        )
        calendar = Calendar.model_construct(matches=matches, n_players=8, n_courts=2)

        is_valid, quality, message = validate_solution(calendar)

        assert is_valid is False
        assert quality == "REJECTED"
        assert "conflict" in message.lower()

    def test_validate_accepts_valid_multi_court_calendar(self):
        """Test that validation accepts valid multi-court calendar."""
        ga = GeneticAlgorithm(
            n_players=8, n_rounds=5, n_courts=2, population_size=20, generations=10
        )
        best_calendar = ga.run(verbose=False)

        is_valid, quality, message = validate_solution(best_calendar)

        assert is_valid is True
        assert quality in ["EXCELLENT", "GOOD", "ACCEPTABLE"]


class TestFitnessWithRounds:
    """Test fitness calculation with multiple courts."""

    def test_fitness_negative_infinity_for_round_conflict(self):
        """Test that calendar with round conflict has -inf fitness."""
        # Use model_construct to bypass validation for testing fitness function
        matches = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # (A,B) vs (C,D)
                [
                    1,
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    1,
                ],  # (A,E) vs (G,H) - A again!
            ]
        )
        calendar = Calendar.model_construct(matches=matches, n_players=8, n_courts=2)

        fitness = calculate_fitness(calendar)

        assert fitness == float("-inf")

    def test_fitness_finite_for_valid_calendar(self):
        """Test that valid calendar has finite fitness."""
        ga = GeneticAlgorithm(
            n_players=8, n_rounds=3, n_courts=2, population_size=5, generations=1
        )
        calendar = ga._generate_valid_calendar()

        fitness = calculate_fitness(calendar)

        assert fitness > float("-inf")


class TestIntegrationMultipleCourts:
    """Integration tests for multiple courts functionality."""

    def test_full_optimization_with_2_courts(self):
        """Test full optimization with 2 courts produces valid result."""
        ga = GeneticAlgorithm(
            n_players=8,
            n_rounds=5,
            n_courts=2,
            population_size=20,
            generations=10,
            early_stopping_patience=5,
        )

        best_calendar = ga.run(verbose=False)

        # Verify result
        assert best_calendar.is_valid()
        assert not best_calendar.has_round_conflicts()
        assert best_calendar.n_courts == 2
        assert best_calendar.get_total_rounds() == 5

        # Check balance
        matches_per_player = best_calendar.get_matches_per_player()
        counts = list(matches_per_player.values())
        max_diff = max(counts) - min(counts)
        assert max_diff <= 2  # Reasonable balance

    def test_8_players_2_courts_all_play_every_round(self):
        """Test that with 8 players and 2 courts, all can play every round."""
        ga = GeneticAlgorithm(
            n_players=8,
            n_rounds=5,
            n_courts=2,
            population_size=50,
            generations=20,
            early_stopping_patience=10,
        )

        best_calendar = ga.run(verbose=False)

        # With 8 players and 2 courts (4 players per match * 2 = 8),
        # ideally all players should play in every round
        waiting_rounds = best_calendar.get_waiting_rounds_per_player()

        total_waiting = sum(sum(gaps) for gaps in waiting_rounds.values())
        # Should have very low or zero waiting
        assert total_waiting <= 5  # Allow some tolerance
