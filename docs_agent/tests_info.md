# Tests Information - American Padel Tournament

## Overview

This document provides detailed information about the test suite, what is being tested, and the testing strategy used in the project.

**Testing Methodology:** Test-Driven Development (TDD)
- Tests are written FIRST, then code is implemented
- Tests define the expected behavior and API
- Tests are never modified to make code pass - code is fixed instead

---

## Test Suite Summary

**Total Tests:** 30
**Status:** ✅ All passing
**Coverage:** Phase 1 - Core Data Structures

### Test Files

1. `tests/test_match.py` - 18 tests
2. `tests/test_calendar.py` - 12 tests

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

## Future Test Additions

### Phase 2: Fitness Function Tests
- Test balance penalty calculation
- Test opponent repetition penalty
- Test team repetition penalty
- Test waiting rounds penalty
- Test early cut bonus
- Test combined fitness function

### Phase 3: Genetic Algorithm Tests
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
**Phase:** 1 - Core Data Structures  
**Test Count:** 30 tests, all passing ✅

