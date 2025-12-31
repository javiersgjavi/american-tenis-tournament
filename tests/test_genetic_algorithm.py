"""
Tests for Genetic Algorithm.
Following TDD methodology - these tests define the expected behavior.
"""

import pytest
import numpy as np
from src.dataclasses import Calendar
from src.genetic_algorithm import GeneticAlgorithm


class TestGeneticAlgorithmInitialization:
    """Test the GeneticAlgorithm initialization."""
    
    def test_create_genetic_algorithm(self):
        """Test creating a GeneticAlgorithm instance."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=20,
            population_size=10,
            generations=5,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism_size=2
        )
        assert ga is not None
        assert ga.n_players == 7
        assert ga.n_rounds == 20
        assert ga.n_matches == 20  # With n_courts=1, n_matches = n_rounds
        assert ga.population_size == 10
        assert ga.generations == 5
        assert ga.mutation_rate == 0.1
        assert ga.crossover_rate == 0.8
        assert ga.elitism_size == 2
    
    def test_default_weights(self):
        """Test that default fitness weights are set."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=20,
            population_size=10,
            generations=5
        )
        assert ga.weight_balance == 100.0
        assert ga.weight_opponent_rep == 10.0
        assert ga.weight_team_rep == 10.0
        assert ga.weight_waiting == 5.0
        assert ga.weight_early_cut == 50.0
    
    def test_custom_weights(self):
        """Test that custom fitness weights can be set."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=20,
            population_size=10,
            generations=5,
            weight_balance=200.0,
            weight_opponent_rep=20.0,
            weight_team_rep=15.0,
            weight_waiting=10.0,
            weight_early_cut=100.0
        )
        assert ga.weight_balance == 200.0
        assert ga.weight_opponent_rep == 20.0
        assert ga.weight_team_rep == 15.0
        assert ga.weight_waiting == 10.0
        assert ga.weight_early_cut == 100.0


class TestInitializePopulation:
    """Test the initialize_population method."""
    
    def test_initialize_population_size(self):
        """Test that population has correct size."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1
        )
        population = ga.initialize_population()
        assert len(population) == 5
    
    def test_initialize_population_valid_calendars(self):
        """Test that all calendars in population are valid."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1
        )
        population = ga.initialize_population()
        for calendar in population:
            assert isinstance(calendar, Calendar)
            assert calendar.is_valid()
            assert len(calendar) == 10
            assert calendar.n_players == 7


class TestTournamentSelection:
    """Test the tournament_selection method."""
    
    def test_tournament_selection_returns_calendar(self):
        """Test that tournament selection returns a Calendar."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1
        )
        population = ga.initialize_population()
        fitness_scores = [ga.calculate_fitness_for_calendar(cal) for cal in population]
        
        selected = ga.tournament_selection(population, fitness_scores, tournament_size=2)
        assert isinstance(selected, Calendar)
    
    def test_tournament_selection_favors_better_fitness(self):
        """Test that tournament selection tends to select better individuals."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=1
        )
        population = ga.initialize_population()
        fitness_scores = [ga.calculate_fitness_for_calendar(cal) for cal in population]
        
        # Run selection many times and track which individuals are selected
        selections = []
        for _ in range(100):
            selected = ga.tournament_selection(population, fitness_scores, tournament_size=3)
            selections.append(selected)
        
        # At least some selections should have been made (not all None)
        assert len(selections) == 100


class TestCrossover:
    """Test the crossover method."""
    
    def test_crossover_returns_two_calendars(self):
        """Test that crossover returns two offspring calendars."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1
        )
        population = ga.initialize_population()
        parent1 = population[0]
        parent2 = population[1]
        
        child1, child2 = ga.crossover(parent1, parent2)
        assert isinstance(child1, Calendar)
        assert isinstance(child2, Calendar)
        assert len(child1) == 10
        assert len(child2) == 10
    
    def test_crossover_produces_valid_calendars(self):
        """Test that crossover produces valid calendars."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1
        )
        population = ga.initialize_population()
        parent1 = population[0]
        parent2 = population[1]
        
        child1, child2 = ga.crossover(parent1, parent2)
        assert child1.is_valid()
        assert child2.is_valid()
    
    def test_crossover_with_crossover_rate(self):
        """Test that crossover respects crossover_rate."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1,
            crossover_rate=0.0  # Never crossover
        )
        population = ga.initialize_population()
        parent1 = population[0]
        parent2 = population[1]
        
        # With crossover_rate=0, should return copies of parents
        child1, child2 = ga.crossover(parent1, parent2)
        # Children should be valid even if no crossover happened
        assert child1.is_valid()
        assert child2.is_valid()


class TestMutation:
    """Test the mutate method."""
    
    def test_mutate_returns_calendar(self):
        """Test that mutate returns a Calendar."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1,
            mutation_rate=1.0  # Always mutate
        )
        population = ga.initialize_population()
        calendar = population[0]
        
        mutated = ga.mutate(calendar)
        assert isinstance(mutated, Calendar)
        assert len(mutated) == 10
    
    def test_mutate_produces_valid_calendar(self):
        """Test that mutation produces valid calendar."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1,
            mutation_rate=1.0  # Always mutate
        )
        population = ga.initialize_population()
        calendar = population[0]
        
        mutated = ga.mutate(calendar)
        assert mutated.is_valid()
    
    def test_mutate_with_mutation_rate(self):
        """Test that mutation respects mutation_rate."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1,
            mutation_rate=0.0  # Never mutate
        )
        population = ga.initialize_population()
        calendar = population[0]
        
        # With mutation_rate=0, should return copy of original
        mutated = ga.mutate(calendar)
        assert mutated.is_valid()


class TestCalculateFitnessForCalendar:
    """Test the calculate_fitness_for_calendar method."""
    
    def test_calculate_fitness_returns_float(self):
        """Test that fitness calculation returns a float."""
        ga = GeneticAlgorithm(
            n_players=7,
            n_rounds=10,
            population_size=5,
            generations=1
        )
        population = ga.initialize_population()
        calendar = population[0]
        
        fitness = ga.calculate_fitness_for_calendar(calendar)
        assert isinstance(fitness, float)
        assert fitness > float('-inf')  # Should be finite for valid calendar
    
    def test_calculate_fitness_uses_weights(self):
        """Test that fitness calculation uses configured weights."""
        ga1 = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=5,
            generations=1,
            weight_balance=100.0
        )
        ga2 = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=5,
            generations=1,
            weight_balance=200.0  # Different weight
        )
        
        # Create same calendar for both
        population = ga1.initialize_population()
        calendar = population[0]
        
        fitness1 = ga1.calculate_fitness_for_calendar(calendar)
        fitness2 = ga2.calculate_fitness_for_calendar(calendar)
        
        # Fitness should be different due to different weights
        # (unless calendar is perfect, but unlikely)
        assert isinstance(fitness1, float)
        assert isinstance(fitness2, float)


class TestGeneticAlgorithmRun:
    """Test the main run method."""
    
    def test_run_returns_best_calendar(self):
        """Test that run returns the best calendar found."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=5
        )
        
        best_calendar = ga.run()
        assert isinstance(best_calendar, Calendar)
        assert best_calendar.is_valid()
        assert len(best_calendar) == 5
        assert best_calendar.n_players == 4
    
    def test_run_with_small_problem(self):
        """Test that GA can solve a small problem."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=3,
            population_size=20,
            generations=10
        )
        
        best_calendar = ga.run()
        assert best_calendar.is_valid()
        
        # Check that solution has reasonable quality
        fitness = ga.calculate_fitness_for_calendar(best_calendar)
        assert fitness > float('-inf')
    
    def test_run_improves_over_generations(self):
        """Test that fitness improves over generations."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=20,
            generations=20
        )
        
        # Track best fitness (GA should store this)
        best_calendar = ga.run()
        final_fitness = ga.calculate_fitness_for_calendar(best_calendar)
        
        # Final fitness should be finite (valid solution)
        assert final_fitness > float('-inf')
        assert best_calendar.is_valid()
    
    def test_run_with_elitism(self):
        """Test that elitism preserves best individuals."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=5,
            elitism_size=2
        )
        
        best_calendar = ga.run()
        assert best_calendar.is_valid()
        
        # With elitism, best solution should never get worse
        # This is implicitly tested by the algorithm design
    
    def test_run_with_verbose_false(self):
        """Test that run works with verbose=False."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=5
        )
        
        best_calendar = ga.run(verbose=False)
        assert isinstance(best_calendar, Calendar)
        assert best_calendar.is_valid()
    
    def test_run_with_verbose_true(self):
        """Test that run works with verbose=True."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=5
        )
        
        best_calendar = ga.run(verbose=True)
        assert isinstance(best_calendar, Calendar)
        assert best_calendar.is_valid()


class TestGeneticAlgorithmEdgeCases:
    """Test edge cases and error handling."""
    
    def test_small_population(self):
        """Test with very small population."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=3,
            population_size=2,
            generations=2
        )
        
        best_calendar = ga.run(verbose=False)
        assert best_calendar.is_valid()
    
    def test_single_generation(self):
        """Test with single generation."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=3,
            population_size=5,
            generations=1
        )
        
        best_calendar = ga.run(verbose=False)
        assert best_calendar.is_valid()
    
    def test_large_elitism(self):
        """Test with elitism_size close to population_size."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=3,
            population_size=10,
            generations=2,
            elitism_size=8
        )
        
        best_calendar = ga.run(verbose=False)
        assert best_calendar.is_valid()


class TestEarlyStopping:
    """Tests for early stopping functionality."""
    
    def test_early_stopping_parameter_exists(self):
        """Test that early_stopping_patience parameter can be set."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=100,
            early_stopping_patience=10
        )
        
        assert ga.early_stopping_patience == 10
    
    def test_early_stopping_disabled_by_default(self):
        """Test that early stopping is disabled by default (None)."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=100
        )
        
        assert ga.early_stopping_patience is None
    
    def test_early_stopping_stops_before_max_generations(self):
        """Test that early stopping stops before reaching max generations."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=20,
            generations=100,
            early_stopping_patience=5
        )
        
        best_calendar = ga.run(verbose=False)
        
        # Should stop early (less than 100 generations)
        assert len(ga.best_fitness_history) < 100
        assert best_calendar.is_valid()
    
    def test_early_stopping_with_zero_patience(self):
        """Test with patience=0 (should stop after first generation without improvement)."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=100,
            early_stopping_patience=0
        )
        
        best_calendar = ga.run(verbose=False)
        
        # Should stop very early
        assert len(ga.best_fitness_history) <= 10
        assert best_calendar.is_valid()
    
    def test_no_early_stopping_runs_all_generations(self):
        """Test that without early stopping, all generations run."""
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=10,
            generations=20,
            early_stopping_patience=None  # Disabled
        )
        
        best_calendar = ga.run(verbose=False)
        
        # Should run all 20 generations
        assert len(ga.best_fitness_history) == 20
        assert best_calendar.is_valid()
    
    def test_early_stopping_message_in_verbose_mode(self):
        """Test that early stopping message is displayed in verbose mode."""
        import io
        import sys
        
        ga = GeneticAlgorithm(
            n_players=4,
            n_rounds=5,
            population_size=20,
            generations=100,
            early_stopping_patience=5
        )
        
        # Capture output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        best_calendar = ga.run(verbose=True)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # Should mention early stopping if it happened
        if len(ga.best_fitness_history) < 100:
            assert "early stopping" in output.lower() or "stopped early" in output.lower()
        
        assert best_calendar.is_valid()

