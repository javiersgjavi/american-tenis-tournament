# Tests Information - American Padel Tournament

## Overview

This document provides detailed information about the test suite, what is being tested, and the testing strategy used in the project.

**Testing Methodology:** Test-Driven Development (TDD)
- Tests are written FIRST, then code is implemented
- Tests define the expected behavior and API
- Tests are never modified to make code pass - code is fixed instead

---

## Test Suite Summary

**Total Tests:** 75
**Status:** ✅ All passing
**Coverage:** Phase 1 (Core Data Structures) + Phase 2 (Fitness Functions) + Phase 3 (Genetic Algorithm)

### Test Files

1. `tests/test_match.py` - 18 tests
2. `tests/test_calendar.py` - 12 tests
3. `tests/test_fitness.py` - 21 tests
4. `tests/test_genetic_algorithm.py` - 24 tests

---

## 1. Match Tests (`tests/test_match.py`)

### 1.1 `TestIsValidMatch` Class (7 tests)

Tests for the `is_valid_match()` utility function.

#### ✅ `test_valid_match_4_players`
- **Purpose:** Verify that a valid match with 4 players is recognized
- **Input:** `[1,1,0,0, 0,0,1,1]` - (A,B) vs (C,D)
- **Expected:** Returns `True`

#### ✅ `test_valid_match_7_players`
- **Purpose:** Verify validation works with 7 players
- **Input:** `[1,0,0,1,0,0,0, 0,1,1,0,0,0,0]` - (A,D) vs (B,C)
- **Expected:** Returns `True`

#### ✅ `test_invalid_match_too_few_players`
- **Purpose:** Reject matches with less than 4 players
- **Input:** `[1,1,0,0, 0,0,1,0]` - Only 3 players
- **Expected:** Returns `False`

#### ✅ `test_invalid_match_too_many_players`
- **Purpose:** Reject matches with more than 4 players
- **Input:** `[1,1,1,0, 0,0,1,1]` - 5 players
- **Expected:** Returns `False`

#### ✅ `test_invalid_match_unbalanced_teams`
- **Purpose:** Reject matches with unbalanced teams
- **Input:** `[1,1,1,0, 0,0,0,1]` - Team 1 has 3, team 2 has 1
- **Expected:** Returns `False`

#### ✅ `test_invalid_match_player_in_both_teams`
- **Purpose:** Reject matches where a player appears in both teams
- **Input:** `[1,1,0,0, 1,0,1,0]` - Player A in both teams
- **Expected:** Returns `False`

#### ✅ `test_invalid_match_empty_teams`
- **Purpose:** Reject completely empty matches
- **Input:** `[0,0,0,0, 0,0,0,0]` - No players
- **Expected:** Returns `False`

---

### 1.2 `TestGenerateRandomMatch` Class (5 tests)

Tests for the `generate_random_match()` utility function.

#### ✅ `test_generates_valid_match_4_players`
- **Purpose:** Verify generated matches are valid for 4 players
- **Expected:** Generated match passes `is_valid_match()`

#### ✅ `test_generates_valid_match_7_players`
- **Purpose:** Verify generated matches are valid for 7 players
- **Expected:** Generated match passes `is_valid_match()`

#### ✅ `test_generates_valid_match_10_players`
- **Purpose:** Verify generated matches are valid for 10 players
- **Expected:** Generated match passes `is_valid_match()`

#### ✅ `test_correct_vector_length`
- **Purpose:** Verify generated match has correct vector length
- **Expected:** Length = `2 * n_players`

#### ✅ `test_generates_different_matches`
- **Purpose:** Verify randomness (not always same match)
- **Method:** Generate 10 matches, check for variety
- **Expected:** At least 2 different matches generated

---

### 1.3 `TestMatch` Class (6 tests)

Tests for the `Match` Pydantic model.

#### ✅ `test_create_valid_match`
- **Purpose:** Verify valid Match instance can be created
- **Input:** Valid match vector
- **Expected:** Match object created successfully

#### ✅ `test_create_invalid_match_raises_error`
- **Purpose:** Verify Pydantic validation rejects invalid matches
- **Input:** Invalid match vector (3 vs 1 players)
- **Expected:** Raises `ValidationError`

#### ✅ `test_is_valid_method`
- **Purpose:** Verify `is_valid()` method works
- **Expected:** Returns `True` for valid match

#### ✅ `test_get_players`
- **Purpose:** Verify `get_players()` returns correct player indices
- **Input:** (A,B) vs (C,D) match
- **Expected:** Returns `{0, 1, 2, 3}` (4 players)

#### ✅ `test_get_teams`
- **Purpose:** Verify `get_teams()` returns correct team separation
- **Input:** (A,D) vs (B,C) match with 7 players
- **Expected:** Team 1 = `{0, 3}`, Team 2 = `{1, 2}`

#### ✅ `test_str_representation`
- **Purpose:** Verify string representation is readable
- **Expected:** Contains "vs", "(", ")" characters

#### ✅ `test_match_with_7_players_scenario`
- **Purpose:** Test realistic scenario with 7 players
- **Input:** (E,F) vs (A,G) = players (4,5) vs (0,6)
- **Expected:** Correct team extraction

---

## 2. Calendar Tests (`tests/test_calendar.py`)

### 2.1 `TestCalendar` Class (12 tests)

Tests for the `Calendar` Pydantic model.

#### ✅ `test_create_valid_calendar`
- **Purpose:** Verify valid Calendar instance can be created
- **Input:** 2 valid matches
- **Expected:** Calendar object created successfully

#### ✅ `test_create_calendar_with_invalid_match_raises_error`
- **Purpose:** Verify Pydantic validation rejects calendars with invalid matches
- **Input:** Calendar with one invalid match
- **Expected:** Raises `ValidationError`

#### ✅ `test_len_method`
- **Purpose:** Verify `__len__()` returns correct number of matches
- **Input:** Calendar with 3 matches
- **Expected:** `len(calendar) == 3`

#### ✅ `test_get_match`
- **Purpose:** Verify `get_match()` returns correct Match object
- **Expected:** Returns Match instance with correct vector

#### ✅ `test_get_match_out_of_bounds`
- **Purpose:** Verify error handling for invalid indices
- **Expected:** Raises `IndexError`

#### ✅ `test_is_valid_method`
- **Purpose:** Verify `is_valid()` method works
- **Expected:** Returns `True` for valid calendar

#### ✅ `test_get_matches_per_player`
- **Purpose:** Verify match counting per player
- **Input:** 3 matches with 7 players
- **Expected:** Correct count for each player:
  - A: 2 matches
  - B: 2 matches
  - C: 2 matches
  - D: 3 matches
  - E: 2 matches
  - F: 1 match
  - G: 0 matches

#### ✅ `test_get_waiting_rounds_per_player`
- **Purpose:** Verify calculation of gaps between matches
- **Input:** 4 matches
- **Example:** Player A plays matches 0 and 3 → waited 2 rounds (matches 1,2)
- **Expected:** Correct gap calculation for all players

#### ✅ `test_empty_calendar`
- **Purpose:** Verify empty calendar is valid
- **Input:** Calendar with 0 matches
- **Expected:** `len() == 0`, all players have 0 matches

#### ✅ `test_single_match_calendar`
- **Purpose:** Verify calendar with single match works
- **Expected:** Valid calendar with 1 match

#### ✅ `test_large_calendar_50_matches`
- **Purpose:** Verify scalability with large calendars
- **Input:** 50 random matches with 7 players
- **Expected:** Valid calendar, all matches valid

---

## Test Coverage by Feature

### ✅ Data Validation
- Valid match structure (4 players, 2 per team)
- Invalid match rejection (too few/many players, unbalanced, overlapping)
- Pydantic automatic validation
- Error handling (ValidationError, IndexError)

### ✅ Match Generation
- Random valid match generation
- Correct vector length
- Randomness verification
- Multiple player counts (4, 7, 10)

### ✅ Match Operations
- Get players from match
- Get teams from match
- String representation
- Validation method

### ✅ Calendar Operations
- Create calendar from matches
- Get individual matches
- Count matches per player
- Calculate waiting rounds per player
- Length method
- Validation method

### ✅ Edge Cases
- Empty calendar
- Single match calendar
- Large calendar (50 matches)
- Out of bounds access
- Invalid data rejection

---

## Testing Strategy

### TDD Workflow Applied

1. **RED:** Write failing test
2. **GREEN:** Implement minimum code to pass
3. **REFACTOR:** Improve code while keeping tests green

### Test Quality Standards

- ✅ Clear, descriptive test names
- ✅ Comprehensive coverage of happy paths
- ✅ Comprehensive coverage of error cases
- ✅ Edge cases included
- ✅ Tests are independent (no dependencies between tests)
- ✅ Tests are deterministic (except randomness tests)

### What We DON'T Test

- Internal implementation details (only public API)
- Third-party library behavior (numpy, pydantic)
- Performance (not yet - may add later)

---

## Running Tests

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test File
```bash
uv run pytest tests/test_match.py -v
uv run pytest tests/test_calendar.py -v
```

### Run Specific Test
```bash
uv run pytest tests/test_match.py::TestMatch::test_get_players -v
```

### Run with Coverage
```bash
uv run pytest tests/ --cov=src --cov-report=html
```

---

## 3. Fitness Tests (`tests/test_fitness.py`)

### 3.1 `TestBalancePenalty` Class (4 tests)

Tests for the `calculate_balance_penalty()` function.

#### ✅ `test_perfect_balance_zero_penalty`
- **Purpose:** Verify perfectly balanced calendar has zero penalty
- **Input:** Calendar where all players play same number of matches
- **Expected:** `penalty == 0.0`

#### ✅ `test_unbalanced_calendar_has_penalty`
- **Purpose:** Verify unbalanced calendar has non-zero penalty
- **Expected:** `penalty > 0.0`

#### ✅ `test_penalty_calculation_formula`
- **Purpose:** Verify penalty follows `(max - min)²` formula
- **Input:** Calendar with max=3, min=0 matches
- **Expected:** `penalty == 9.0` (3² = 9)

#### ✅ `test_empty_calendar_zero_penalty`
- **Purpose:** Verify empty calendar has zero penalty
- **Expected:** `penalty == 0.0`

---

### 3.2 `TestOpponentRepetitionPenalty` Class (3 tests)

Tests for the `calculate_opponent_repetition_penalty()` function.

#### ✅ `test_no_repetitions_zero_penalty`
- **Purpose:** Verify no repetitions gives zero penalty
- **Expected:** `penalty == 0.0`

#### ✅ `test_one_repetition_has_penalty`
- **Purpose:** Verify repeated opponent pairings have penalty
- **Expected:** Correct penalty calculation for repetitions

#### ✅ `test_multiple_repetitions_quadratic_penalty`
- **Purpose:** Verify penalty grows quadratically
- **Input:** Same match repeated 3 times
- **Expected:** `penalty == 16.0` (4 pairs × (3-1)² = 16)

---

### 3.3 `TestTeamRepetitionPenalty` Class (3 tests)

Tests for the `calculate_team_repetition_penalty()` function.

#### ✅ `test_no_repetitions_zero_penalty`
- **Purpose:** Verify no team repetitions gives zero penalty
- **Expected:** `penalty == 0.0`

#### ✅ `test_one_repetition_has_penalty`
- **Purpose:** Verify repeated team pairings have penalty
- **Expected:** `penalty == 1.0` for one repetition

#### ✅ `test_multiple_repetitions_quadratic_penalty`
- **Purpose:** Verify penalty grows quadratically
- **Input:** Same teams repeated 3 times
- **Expected:** `penalty == 8.0` (2 teams × (3-1)² = 8)

---

### 3.4 `TestWaitingPenalty` Class (3 tests)

Tests for the `calculate_waiting_penalty()` function.

#### ✅ `test_consecutive_matches_zero_penalty`
- **Purpose:** Verify consecutive matches have zero waiting
- **Expected:** `penalty == 0.0`

#### ✅ `test_one_gap_has_penalty`
- **Purpose:** Verify waiting one round has penalty
- **Expected:** Correct gap calculation

#### ✅ `test_multiple_gaps_quadratic_penalty`
- **Purpose:** Verify penalty is quadratic in gap size
- **Input:** Player waits 2 rounds (gap=2)
- **Expected:** `penalty == 8.0` (2 players × 2² = 8)

---

### 3.5 `TestEarlyCutBonus` Class (4 tests)

Tests for the `calculate_early_cut_bonus()` function.

#### ✅ `test_perfect_cut_at_first_match_high_bonus`
- **Purpose:** Verify early perfect cut gives high bonus
- **Expected:** `bonus >= 1000.0`

#### ✅ `test_perfect_cut_later_lower_bonus`
- **Purpose:** Verify later cuts give lower bonus
- **Expected:** Bonus decreases with cut position

#### ✅ `test_no_cut_points_zero_bonus`
- **Purpose:** Verify calendar with no cuts has appropriate bonus
- **Expected:** `bonus > 0.0` for acceptable cuts

#### ✅ `test_multiple_perfect_cuts_additional_bonus`
- **Purpose:** Verify multiple cuts give additional bonus
- **Expected:** `bonus > 1000.0` with additional bonuses

---

### 3.6 `TestCombinedFitness` Class (4 tests)

Tests for the `calculate_fitness()` function.

#### ✅ `test_invalid_calendar_negative_infinity`
- **Purpose:** Verify invalid calendars get worst fitness
- **Expected:** Valid calendars have finite fitness

#### ✅ `test_perfect_calendar_high_fitness`
- **Purpose:** Verify perfect calendars have high fitness
- **Expected:** `fitness > 1000.0`

#### ✅ `test_fitness_with_custom_weights`
- **Purpose:** Verify custom weights affect fitness
- **Expected:** Different weights produce different fitness

#### ✅ `test_fitness_comparison`
- **Purpose:** Verify better calendars have higher fitness
- **Expected:** Balanced calendar > unbalanced calendar

---

## 4. Genetic Algorithm Tests (`tests/test_genetic_algorithm.py`)

### 4.1 `TestGeneticAlgorithmInitialization` Class (3 tests)

Tests for GA initialization and configuration.

#### ✅ `test_create_genetic_algorithm`
- **Purpose:** Verify GA instance can be created with all parameters
- **Expected:** All parameters correctly set

#### ✅ `test_default_weights`
- **Purpose:** Verify default fitness weights are set correctly
- **Expected:** Default weights match specification

#### ✅ `test_custom_weights`
- **Purpose:** Verify custom fitness weights can be configured
- **Expected:** Custom weights are applied

---

### 4.2 `TestInitializePopulation` Class (2 tests)

Tests for population initialization.

#### ✅ `test_initialize_population_size`
- **Purpose:** Verify population has correct size
- **Expected:** Population size matches configuration

#### ✅ `test_initialize_population_valid_calendars`
- **Purpose:** Verify all calendars in population are valid
- **Expected:** All calendars pass validation

---

### 4.3 `TestTournamentSelection` Class (2 tests)

Tests for tournament selection operator.

#### ✅ `test_tournament_selection_returns_calendar`
- **Purpose:** Verify selection returns a Calendar object
- **Expected:** Returns valid Calendar instance

#### ✅ `test_tournament_selection_favors_better_fitness`
- **Purpose:** Verify selection tends to pick better individuals
- **Expected:** Selection works correctly over multiple runs

---

### 4.4 `TestCrossover` Class (3 tests)

Tests for crossover operator.

#### ✅ `test_crossover_returns_two_calendars`
- **Purpose:** Verify crossover returns two offspring
- **Expected:** Returns two Calendar objects

#### ✅ `test_crossover_produces_valid_calendars`
- **Purpose:** Verify crossover produces valid calendars
- **Expected:** Both offspring are valid

#### ✅ `test_crossover_with_crossover_rate`
- **Purpose:** Verify crossover respects crossover_rate
- **Expected:** Works correctly with rate=0.0

---

### 4.5 `TestMutation` Class (3 tests)

Tests for mutation operator.

#### ✅ `test_mutate_returns_calendar`
- **Purpose:** Verify mutation returns a Calendar
- **Expected:** Returns valid Calendar instance

#### ✅ `test_mutate_produces_valid_calendar`
- **Purpose:** Verify mutation produces valid calendar
- **Expected:** Mutated calendar is valid

#### ✅ `test_mutate_with_mutation_rate`
- **Purpose:** Verify mutation respects mutation_rate
- **Expected:** Works correctly with rate=0.0

---

### 4.6 `TestCalculateFitnessForCalendar` Class (2 tests)

Tests for fitness calculation method.

#### ✅ `test_calculate_fitness_returns_float`
- **Purpose:** Verify fitness calculation returns float
- **Expected:** Returns finite float for valid calendar

#### ✅ `test_calculate_fitness_uses_weights`
- **Purpose:** Verify fitness uses configured weights
- **Expected:** Different weights produce different fitness

---

### 4.7 `TestGeneticAlgorithmRun` Class (6 tests)

Tests for main GA loop.

#### ✅ `test_run_returns_best_calendar`
- **Purpose:** Verify run returns best calendar found
- **Expected:** Returns valid Calendar instance

#### ✅ `test_run_with_small_problem`
- **Purpose:** Verify GA can solve small problem
- **Expected:** Returns valid solution with reasonable fitness

#### ✅ `test_run_improves_over_generations`
- **Purpose:** Verify fitness improves over generations
- **Expected:** Final fitness is finite and valid

#### ✅ `test_run_with_elitism`
- **Purpose:** Verify elitism preserves best individuals
- **Expected:** Returns valid solution

#### ✅ `test_run_with_verbose_false`
- **Purpose:** Verify run works with verbose=False
- **Expected:** Runs without printing progress

#### ✅ `test_run_with_verbose_true`
- **Purpose:** Verify run works with verbose=True
- **Expected:** Runs with progress output

---

### 4.8 `TestGeneticAlgorithmEdgeCases` Class (3 tests)

Tests for edge cases and error handling.

#### ✅ `test_small_population`
- **Purpose:** Verify GA works with very small population
- **Expected:** Returns valid solution

#### ✅ `test_single_generation`
- **Purpose:** Verify GA works with single generation
- **Expected:** Returns valid solution

#### ✅ `test_large_elitism`
- **Purpose:** Verify GA works with large elitism size
- **Expected:** Returns valid solution

---

## Future Test Additions

### Phase 4: Cut Points Detection Tests
- Test population initialization
- Test selection methods
- Test crossover operations
- Test mutation operations
- Test elitism
- Test GA convergence

### Phase 4: Cut Points Tests
- Test perfect cut detection
- Test acceptable cut detection
- Test solution validation
- Test quality criteria

### Phase 5: Output Tests
- Test match vector to string conversion
- Test calendar printing
- Test statistics formatting
- Test CSV export

---

## Test Maintenance

### When to Update Tests

- ✅ When requirements change
- ✅ When bugs are found (add regression test)
- ✅ When new features are added

### When NOT to Update Tests

- ❌ When code doesn't pass tests (fix code, not tests)
- ❌ When refactoring (tests should still pass)
- ❌ To make tests "easier to pass"

---

**Last Updated:** 2025-11-29  
**Phase:** 3 - Genetic Algorithm  
**Test Count:** 75 tests, all passing ✅

