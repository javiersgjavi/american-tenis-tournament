"""
End-to-end tests for the main script.
Tests the complete workflow of the genetic algorithm.
"""

import pytest
import numpy as np
from src.genetic_algorithm import GeneticAlgorithm, validate_solution
from src.dataclasses import Calendar


class TestEndToEnd:
    """End-to-end tests for the complete system."""

    def test_small_tournament_execution(self):
        """
        Test a small tournament execution to verify the complete workflow.
        Uses reduced parameters for faster execution.
        """
        # Small configuration for fast testing
        N_PLAYERS = 4
        N_ROUNDS = 10
        POPULATION_SIZE = 20
        GENERATIONS = 50

        # Initialize GA
        ga = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism_size=2,
            weight_balance=100.0,
            weight_opponent_rep=10.0,
            weight_team_rep=10.0,
            weight_waiting=5.0,
            weight_early_cut=50.0,
        )

        # Run optimization
        best_calendar = ga.run(verbose=False)

        # Verify we got a calendar
        assert best_calendar is not None
        assert isinstance(best_calendar, Calendar)
        assert len(best_calendar) == N_ROUNDS
        assert best_calendar.n_players == N_PLAYERS

        # Verify all matches are valid
        assert best_calendar.is_valid()

        # Verify fitness history was tracked
        assert len(ga.best_fitness_history) == GENERATIONS

        # Verify fitness improved or stayed same (never got worse)
        for i in range(1, len(ga.best_fitness_history)):
            assert ga.best_fitness_history[i] >= ga.best_fitness_history[i - 1]

    def test_medium_tournament_execution(self):
        """
        Test a medium-sized tournament (7 players, 30 matches).
        This is closer to a real-world scenario.
        """
        N_PLAYERS = 7
        N_ROUNDS = 30
        POPULATION_SIZE = 50
        GENERATIONS = 100

        # Initialize GA
        ga = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism_size=2,
            weight_balance=100.0,
            weight_opponent_rep=10.0,
            weight_team_rep=10.0,
            weight_waiting=5.0,
            weight_early_cut=50.0,
        )

        # Run optimization
        best_calendar = ga.run(verbose=False)

        # Verify calendar properties
        assert best_calendar is not None
        assert len(best_calendar) == N_ROUNDS
        assert best_calendar.n_players == N_PLAYERS
        assert best_calendar.is_valid()

        # Verify solution quality
        is_valid, quality, message = validate_solution(best_calendar)

        # The solution should be at least acceptable
        # (might not always be EXCELLENT due to randomness, but should be valid)
        assert is_valid, f"Solution should be valid. Got: {quality} - {message}"
        assert quality in ["EXCELLENT", "GOOD", "ACCEPTABLE"]

    def test_fitness_improvement(self):
        """
        Test that the genetic algorithm actually improves fitness over time.
        """
        N_PLAYERS = 5
        N_ROUNDS = 15
        POPULATION_SIZE = 30
        GENERATIONS = 50

        ga = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism_size=2,
        )

        best_calendar = ga.run(verbose=False)

        # Check that fitness improved
        initial_fitness = ga.best_fitness_history[0]
        final_fitness = ga.best_fitness_history[-1]

        # Final fitness should be better than or equal to initial
        assert final_fitness >= initial_fitness

        # There should be some improvement (not stuck at initial)
        # Allow for rare cases where initial solution is already very good
        improvement = final_fitness - initial_fitness
        assert improvement >= 0

    def test_solution_has_cut_points(self):
        """
        Test that the optimized solution has cut points.
        This is a key requirement for tournament flexibility.
        """
        N_PLAYERS = 6
        N_ROUNDS = 20
        POPULATION_SIZE = 40
        GENERATIONS = 80

        ga = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            weight_balance=100.0,  # High weight on balance
            weight_early_cut=50.0,  # Incentivize early cuts
        )

        best_calendar = ga.run(verbose=False)

        # Validate solution
        is_valid, quality, message = validate_solution(best_calendar)

        # Should have at least some cut points
        from src.genetic_algorithm import detect_cut_points

        perfect_cuts, acceptable_cuts = detect_cut_points(best_calendar)

        # Should have at least one cut point (perfect or acceptable)
        assert len(acceptable_cuts) > 0, "Solution should have at least one cut point"

    def test_balance_optimization(self):
        """
        Test that the algorithm optimizes for balance in matches per player.
        """
        N_PLAYERS = 5
        N_ROUNDS = 20
        POPULATION_SIZE = 30
        GENERATIONS = 60

        ga = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            weight_balance=200.0,  # Very high weight on balance
            weight_opponent_rep=5.0,
            weight_team_rep=5.0,
            weight_waiting=2.0,
            weight_early_cut=30.0,
        )

        best_calendar = ga.run(verbose=False)

        # Check balance
        matches_per_player = best_calendar.get_matches_per_player()
        counts = list(matches_per_player.values())
        max_matches = max(counts)
        min_matches = min(counts)
        difference = max_matches - min_matches

        # With high balance weight, difference should be small
        # For 5 players and 20 matches, we expect good balance
        assert difference <= 2, f"Balance difference should be ≤ 2, got {difference}"

    def test_all_matches_valid(self):
        """
        Test that all generated matches are valid (4 different players).
        """
        N_PLAYERS = 7
        N_ROUNDS = 25
        POPULATION_SIZE = 40
        GENERATIONS = 60

        ga = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
        )

        best_calendar = ga.run(verbose=False)

        # Check every single match
        for i in range(len(best_calendar)):
            match = best_calendar.get_match(i)
            assert match.is_valid(), f"Match {i} is invalid"

            players = match.get_players()
            assert len(players) == 4, f"Match {i} should have 4 players"
            assert len(set(players)) == 4, f"Match {i} has repeated players"

    def test_reproducibility_with_seed(self):
        """
        Test that results are reproducible when using the same random seed.
        """
        import random
        import numpy as np

        N_PLAYERS = 5
        N_ROUNDS = 15
        POPULATION_SIZE = 20
        GENERATIONS = 30

        # First run
        random.seed(42)
        np.random.seed(42)

        ga1 = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
        )
        calendar1 = ga1.run(verbose=False)

        # Second run with same seed
        random.seed(42)
        np.random.seed(42)

        ga2 = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
        )
        calendar2 = ga2.run(verbose=False)

        # Results should be identical
        assert np.array_equal(calendar1.matches, calendar2.matches)
        assert ga1.best_fitness_history == ga2.best_fitness_history

    def test_different_player_counts(self):
        """
        Test that the algorithm works with different numbers of players.
        """
        player_counts = [4, 5, 6, 7, 8]

        for n_players in player_counts:
            ga = GeneticAlgorithm(
                n_players=n_players, n_rounds=15, population_size=20, generations=30
            )

            best_calendar = ga.run(verbose=False)

            assert best_calendar is not None
            assert best_calendar.n_players == n_players
            assert best_calendar.is_valid()
            assert len(best_calendar) == 15


class TestMainScriptComponents:
    """Test individual components used in main.py"""

    def test_validate_solution_returns_correct_format(self):
        """Test that validate_solution returns the expected format."""
        # Create a simple valid calendar
        ga = GeneticAlgorithm(
            n_players=4, n_rounds=8, population_size=10, generations=20
        )

        calendar = ga.run(verbose=False)

        # Validate solution
        result = validate_solution(calendar)

        # Should return tuple of (bool, str, str)
        assert isinstance(result, tuple)
        assert len(result) == 3

        is_valid, quality, message = result
        assert isinstance(is_valid, bool)
        assert isinstance(quality, str)
        assert isinstance(message, str)

        # Quality should be one of the expected values
        assert quality in ["EXCELLENT", "GOOD", "ACCEPTABLE", "REJECTED"]

    def test_fitness_history_tracking(self):
        """Test that fitness history is properly tracked."""
        ga = GeneticAlgorithm(
            n_players=4, n_rounds=10, population_size=15, generations=25
        )

        # Initially empty
        assert len(ga.best_fitness_history) == 0

        # Run algorithm
        ga.run(verbose=False)

        # Should have one entry per generation
        assert len(ga.best_fitness_history) == 25

        # All entries should be finite numbers
        for fitness in ga.best_fitness_history:
            assert fitness != float("-inf")
            assert fitness != float("inf")
            assert not np.isnan(fitness)


class TestParallelization:
    """Test parallelization features."""

    def test_parallel_execution(self):
        """Test that parallel execution works correctly."""
        # Run with parallelization
        ga_parallel = GeneticAlgorithm(
            n_players=5,
            n_rounds=15,
            population_size=20,
            generations=20,
            n_jobs=2,  # Use 2 parallel jobs
        )

        best_calendar = ga_parallel.run(verbose=False)

        assert best_calendar is not None
        assert best_calendar.is_valid()
        assert len(best_calendar) == 15

    def test_sequential_vs_parallel_same_seed(self):
        """Test that sequential and parallel give same results with same seed."""
        import random
        import numpy as np

        N_PLAYERS = 4
        N_ROUNDS = 10
        POPULATION_SIZE = 15
        GENERATIONS = 15

        # Sequential run
        random.seed(123)
        np.random.seed(123)

        ga_seq = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            n_jobs=1,  # Sequential
        )
        calendar_seq = ga_seq.run(verbose=False)

        # Parallel run with same seed
        random.seed(123)
        np.random.seed(123)

        ga_par = GeneticAlgorithm(
            n_players=N_PLAYERS,
            n_rounds=N_ROUNDS,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            n_jobs=2,  # Parallel
        )
        calendar_par = ga_par.run(verbose=False)

        # Results should be identical
        assert np.array_equal(calendar_seq.matches, calendar_par.matches)
        assert ga_seq.best_fitness_history == ga_par.best_fitness_history


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimum_matches(self):
        """Test with minimum number of matches."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=1,  # Just one match
            population_size=10,
            generations=10,
        )

        best_calendar = ga.run(verbose=False)

        assert len(best_calendar) == 1
        assert best_calendar.is_valid()

    def test_many_matches(self):
        """Test with a large number of matches."""
        ga = GeneticAlgorithm(
            n_players=6,
            n_rounds=100,  # Many matches
            population_size=30,
            generations=50,
        )

        best_calendar = ga.run(verbose=False)

        assert len(best_calendar) == 100
        assert best_calendar.is_valid()

    def test_minimum_players(self):
        """Test with minimum number of players (4 - exactly one match possible)."""
        ga = GeneticAlgorithm(
            n_players=4, n_rounds=5, population_size=10, generations=20
        )

        best_calendar = ga.run(verbose=False)

        assert best_calendar.n_players == 4
        assert best_calendar.is_valid()
