# Implementation Details - American Padel Tournament

## 📁 File Organization

The project is organized into multiple files for better modularity:

```
american-tenis-tournament/
├── src/
│   ├── dataclasses.py          # Match and Calendar Pydantic models
│   ├── utils.py                # Utility functions (generation, validation)
│   ├── genetic_algorithm.py    # GA logic and fitness functions
│   └── printer.py              # Output formatting
├── tests/
│   ├── test_match.py           # Tests for Match class
│   ├── test_calendar.py        # Tests for Calendar class
│   ├── test_fitness.py         # Tests for fitness functions
│   └── test_genetic_algorithm.py  # Tests for GA
├── docs_agent/
│   ├── agent.md                # Project overview and concepts
│   ├── implementation.md       # This file - implementation details
│   ├── changelog.md            # Progress tracking and changes
│   └── tests_info.md           # Test suite documentation
├── main.py                     # Main execution script
├── tournament.ipynb            # Jupyter notebook for easy execution
└── README.md
```

## 🏗️ Code Structure

### 1. `src/dataclasses.py`

Contains Pydantic data models for Match and Calendar.

#### Classes

**Match (Pydantic Model)**
- Represents a single match with vector encoding
- Automatic validation using `@field_validator` decorator (Pydantic v2)
- Methods: `is_valid()`, `get_players()`, `get_teams()`, `__str__()`
- Type hints: Uses native Python types (`list[int]`, `tuple[list[int], list[int]]`)

**Calendar (Pydantic Model)**
- Represents complete tournament calendar (matrix of matches)
- Automatic validation of all matches
- Methods: `get_match()`, `get_matches_per_player()`, `get_waiting_rounds_per_player()`, `is_valid()`, `__len__()`
- Type hints: Uses native Python types (`dict[int, int]`, `dict[int, list[int]]`)

### 2. `src/utils.py`

Contains utility functions for match generation and validation.

#### Functions

**Match Generation & Validation:**
- `generate_random_match(n_players: int) -> np.ndarray` - Generate random valid match vector
- `is_valid_match(match_vector: np.ndarray) -> bool` - Check if match has exactly 4 different players

### 3. `src/genetic_algorithm.py`

Contains GA logic and fitness functions (to be implemented in phases 2-3).

#### Classes (Phase 3)

**GeneticAlgorithm**
- Main GA implementation with configurable parameters
- Methods: `initialize_population()`, `calculate_fitness()`, `tournament_selection()`, `crossover()`, `mutate()`, `run()`
- Returns: `(best_calendar, is_valid, message)` from `run()`

#### Functions (Phase 2)

**Fitness Components:**
- `calculate_balance_penalty()` - Penalty for unbalanced matches per player
- `calculate_opponent_repetition_penalty()` - Penalty for repeated opponents
- `calculate_team_repetition_penalty()` - Penalty for repeated teams
- `calculate_waiting_penalty()` - Penalty for players waiting too long
- `calculate_early_cut_bonus()` - Bonus for early cut points

**Analysis & Validation (Phase 4):**
- `detect_cut_points()` - Find perfect and acceptable cut points
- `validate_solution()` - Validate final solution quality

### 4. `src/printer.py`

Handles all output formatting and visualization.

#### Functions

- `match_vector_to_string()` - Convert match vector to readable format: `(A,D) vs (B,C)`
- `print_calendar()` - Print complete match calendar
- `print_statistics()` - Print matches per player and other stats
- `print_cut_points()` - Print perfect and acceptable cut points
- `print_results()` - Print complete formatted output
- `export_to_csv()` - Export calendar to CSV file (optional)

### 5. `main.py` (root directory)

Main execution script that ties everything together.

#### Structure

**Configuration parameters:**
- `N_PLAYERS = 7` - Number of players
- `N_MATCHES = 50` - Matches to generate
- `POPULATION_SIZE = 100` - GA population size
- `GENERATIONS = 200` - Number of iterations
- `MUTATION_RATE = 0.1` - Probability of mutation
- `CROSSOVER_RATE = 0.8` - Probability of crossover
- `ELITISM_SIZE = 2` - Best individuals to preserve

**Fitness weights:**
- `WEIGHT_BALANCE = 100.0` - Most important
- `WEIGHT_OPPONENT_REP = 10.0`
- `WEIGHT_TEAM_REP = 10.0`
- `WEIGHT_WAITING = 5.0`
- `WEIGHT_EARLY_CUT = 50.0` - Bonus for early cuts

**Main execution flow:**
```
1. Configure parameters and weights
2. Initialize GeneticAlgorithm with config
3. Run optimization → (best_calendar, is_valid, message)
4. If not valid:
   - Print error message
   - Suggest improvements (more generations, larger population, etc.)
   - Exit
5. If valid:
   - Print success message
   - Print formatted results
```

### 6. `tournament.ipynb` (root directory)

Jupyter notebook for interactive execution and experimentation.

#### Notebook Cells

1. **Imports and Setup**
2. **Configuration Parameters** (easy to modify)
3. **Run Genetic Algorithm**
4. **Display Results**
5. **Analysis and Visualization** (optional charts)
6. **Export Results** (optional)

## 📝 Implementation Notes

### Matrix Representation

- Calendar shape: `(N_MATCHES, 2 * N_PLAYERS)`
- Each row is a match
- First N_PLAYERS bits: team 1
- Next N_PLAYERS bits: team 2
- Exactly 4 ones per row (2 per team)

**Example with 7 players:**
```python
# Match: (A,D) vs (B,C)
match_vector = [1,0,0,1,0,0,0, 0,1,1,0,0,0,0]
#               A B C D E F G   A B C D E F G
#               [  Team 1   ]   [  Team 2   ]
```

### Match Validation

Every match must satisfy:
1. Exactly 4 ones in the vector (4 players)
2. Exactly 2 ones in first half (team 1)
3. Exactly 2 ones in second half (team 2)
4. No overlap between teams (no player in both)

**Validation logic:**
```
sum(team1) == 2 AND sum(team2) == 2 AND no_overlap(team1, team2)
```

### Fitness Calculation Details

#### 1. Balance Penalty
**Formula:**
```
penalty = (max_matches - min_matches)²
```
Where `max_matches` and `min_matches` are the maximum and minimum number of matches played by any player.

#### 2. Opponent Repetition Penalty
**Algorithm:**
1. Count how many times each pair of players face each other
2. For each pair, calculate `(count - 1)²`
3. Sum all penalties

**Formula:**
```
penalty = Σ (opponent_count[pair] - 1)² for all opponent pairs
```

#### 3. Team Repetition Penalty
**Algorithm:**
1. Count how many times each pair of players play together
2. For each pair, calculate `(count - 1)²`
3. Sum all penalties

**Formula:**
```
penalty = Σ (team_count[pair] - 1)² for all team pairs
```

#### 4. Waiting Rounds Penalty
**Algorithm:**
1. For each player, find all match indices where they play
2. Calculate gaps between consecutive matches
3. Square each gap and sum

**Formula:**
```
penalty = Σ Σ (gap_between_matches)² for all players and their gaps
```

**Example:** Player A plays matches [1, 5, 8] → gaps are [3, 2] → penalty = 3² + 2² = 13

#### 5. Early Cut Point Bonus
**Algorithm:**
1. Detect all perfect and acceptable cut points
2. Reward inversely proportional to position of first cut
3. Additional bonus for multiple early cuts

**Formula:**
```
bonus = 1000 / (first_perfect_cut + 1) + additional_bonuses
```

**Rationale:** A cut at match 7 gives bonus ≈ 125, while a cut at match 28 gives bonus ≈ 35

### Solution Validation

**Validation Criteria:**

1. **All matches are valid** (4 different players each)
2. **At least one cut point exists** (perfect or acceptable)
3. **Balance is reasonable** (max difference ≤ 2 matches)
4. **First cut point is early enough** (before 60% of calendar)

**Quality Levels:**
- **EXCELLENT:** First perfect cut in first 30% of matches
- **GOOD:** First perfect cut in first 50% of matches
- **ACCEPTABLE:** First acceptable cut in first 60% of matches
- **REJECTED:** No cut points or first cut after 60%

**Return format:** `(is_valid: bool, message: str)`

### Genetic Operators Implementation

#### Initialization
**Algorithm:**
1. Create `population_size` empty calendars
2. For each calendar, generate `n_matches` random valid matches
3. Validate each calendar using Pydantic

**Pseudocode:**
```
for i in 1..population_size:
    calendar[i] = []
    for j in 1..n_matches:
        calendar[i].append(generate_random_match())
    validate(calendar[i])
```

#### Crossover (Single-Point)
**Algorithm:**
1. Select random crossover point
2. Child1 = Parent1[0:point] + Parent2[point:end]
3. Child2 = Parent2[0:point] + Parent1[point:end]

**Pseudocode:**
```
if random() < crossover_rate:
    point = random(1, n_matches-1)
    child1 = parent1[:point] ⊕ parent2[point:]
    child2 = parent2[:point] ⊕ parent1[point:]
```

#### Mutation
**Three mutation types (random choice):**

1. **Replace Match:** Replace one match with a new random valid match
2. **Swap Matches:** Swap the order of two matches in the calendar
3. **Regenerate Match:** Completely regenerate a random match

**Pseudocode:**
```
if random() < mutation_rate:
    type = random_choice(['replace', 'swap', 'regenerate'])
    if type == 'replace':
        idx = random(0, n_matches)
        calendar[idx] = generate_random_match()
    elif type == 'swap':
        idx1, idx2 = random_sample(2)
        swap(calendar[idx1], calendar[idx2])
    elif type == 'regenerate':
        idx = random(0, n_matches)
        calendar[idx] = generate_random_match()
```

#### Main GA Loop
**Algorithm:**
```
1. Initialize population
2. For each generation:
   a. Calculate fitness for all individuals
   b. Track best individual
   c. Select elite individuals (elitism)
   d. Generate offspring:
      - Select parents (tournament selection)
      - Apply crossover
      - Apply mutation
   e. Create new generation (elite + offspring)
   f. Print progress every 10 generations
3. Validate final best solution
4. Return (best_calendar, is_valid, message)
```

**Key Points:**
- Elitism ensures best solutions are preserved
- Tournament selection favors better individuals
- Progress tracking helps monitor convergence
- Final validation ensures solution quality

## ✅ Implementation Tasks

### Phase 1: Core Data Structures ✅
- [x] Implement `Match` class
- [x] Implement `Calendar` class
- [x] Implement `generate_random_match()` function
- [x] Implement `is_valid_match()` function
- [x] Add unit tests in `tests/test_match.py` and `tests/test_calendar.py`

### Phase 2: Fitness Function ⏳
- [ ] Implement `calculate_balance_penalty()`
- [ ] Implement `calculate_opponent_repetition_penalty()`
- [ ] Implement `calculate_team_repetition_penalty()`
- [ ] Implement `calculate_waiting_penalty()`
- [ ] Implement `calculate_early_cut_bonus()` (NEW - incentivize early cut points)
- [ ] Implement combined fitness function with all penalties + early cut bonus
- [ ] Add tests in `tests/test_fitness.py`

### Phase 3: Genetic Algorithm ⏳
- [ ] Implement `GeneticAlgorithm` class
- [ ] Implement `initialize_population()`
- [ ] Implement `tournament_selection()`
- [ ] Implement `crossover()`
- [ ] Implement `mutate()`
- [ ] Implement main GA loop with elitism
- [ ] Add progress tracking
- [ ] Add tests in `tests/test_genetic_algorithm.py`

### Phase 4: Cut Points Detection ⏳
- [ ] Implement `detect_cut_points()` function
- [ ] Implement `validate_solution()` function (check quality and cut points)
- [ ] Test with sample calendars

### Phase 5: Output Formatting ⏳
- [ ] Implement `match_vector_to_string()`
- [ ] Implement `print_calendar()`
- [ ] Implement `print_statistics()`
- [ ] Implement `print_cut_points()`
- [ ] Implement `print_results()`
- [ ] Optional: Implement `export_to_csv()`

### Phase 6: Main Script and Notebook ⏳
- [ ] Create `main.py` with configuration
- [ ] Create `tournament.ipynb` notebook
- [ ] Test end-to-end execution
- [ ] Add documentation and comments

### Phase 7: Testing and Optimization ⏳
- [ ] Test with different player counts (4, 6, 7, 8, 10)
- [ ] Test with different match counts
- [ ] Tune fitness weights
- [ ] Tune GA parameters
- [ ] Performance optimization if needed

## 🎯 Current Status

**Status:** Phase 1 Complete - Core Data Structures Implemented  
**Last Updated:** 2025-11-29  
**Next Steps:** Begin implementation of Phase 2 (Fitness Function)

## 📊 Implementation Progress

- [x] Phase 1: Core Data Structures ✅
- [ ] Phase 2: Fitness Function
- [ ] Phase 3: Genetic Algorithm
- [ ] Phase 4: Cut Points Detection
- [ ] Phase 5: Output Formatting
- [ ] Phase 6: Main Script and Notebook
- [ ] Phase 7: Testing and Optimization

## 🔧 Technical Decisions

### Project Management
- **Package Manager:** `uv` for fast dependency management and execution
- **Python Version:** 3.10+

### Libraries Used
- `numpy`: For efficient matrix operations
- `pydantic`: For data validation and beautiful class definitions
- `typing`: For type hints throughout the codebase
- `random`: For randomization in GA
- `collections.defaultdict`: For counting repetitions

### Design Patterns
- **Pydantic models** for Match and Calendar classes (validation + clean code)
- **Type hints everywhere** for better code quality and IDE support
- **Class-based design** for Match, Calendar, and GeneticAlgorithm
- **Functional approach** for utility functions
- **Separation of concerns** between logic and presentation

### Performance Considerations
- Use numpy arrays for calendar representation (fast operations)
- Cache fitness calculations if needed
- Consider parallelization for large populations

### Code Quality
- Use `pydantic` for automatic validation of data structures
- Use native Python type hints (`list[int]`, `dict[str, int]`) instead of `typing` module when possible
- Type annotations for all functions and methods
- Validate final solution before returning results
- Clear error messages when solution is invalid or suboptimal

### Testing Methodology

**Test-Driven Development (TDD):**
- **Write tests FIRST**, then implement the code
- Tests define the expected behavior and API
- **NEVER modify tests to make code pass** - fix the code instead
- Goal: Write good code that passes well-defined tests, not tests that pass bad code

**TDD Workflow:**
1. Write test for a feature (test will fail - RED)
2. Implement minimum code to pass the test (GREEN)
3. Refactor code while keeping tests passing (REFACTOR)
4. Repeat

**Test Quality:**
- Tests must be clear and comprehensive
- Cover edge cases and error conditions
- Tests are the specification - they don't change unless requirements change
- If a test fails, the code is wrong, not the test

## 🚀 Running the Project

### Using uv (Recommended)

```bash
# Install dependencies
uv sync

# Run main script
uv run python main.py

# Run jupyter notebook
uv run jupyter notebook tournament.ipynb
```

---

**Version:** 1.0  
**Last Modified:** 2025-11-29

