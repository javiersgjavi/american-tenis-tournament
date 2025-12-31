# American Padel Tournament - Genetic Algorithm

## 📋 Project Overview

This project implements a calendar generator for American-style padel tournaments using genetic algorithms. The goal is to create an optimized list of matches that balances player participation and minimizes unwanted repetitions.

## 🎯 Main Objective

Generate a match calendar that:
- Balances the number of matches per player
- Minimizes team repetitions
- Minimizes opponent repetitions
- Minimizes waiting rounds for players
- Identifies optimal cut points to finish the tournament

## 🎾 Multiple Courts Support

### Court Configuration
The tournament can be configured to use multiple courts simultaneously:
- `n_courts = 1`: Sequential play (one match at a time) - default behavior
- `n_courts = 2`: Two matches played simultaneously per round
- `n_courts = N`: N matches played simultaneously per round

### Round Concept
With multiple courts, matches are grouped into **rounds**:
- Each round contains up to `n_courts` matches played simultaneously
- Example with 8 players and 2 courts:
  - Round 1: Court 1: (A,B) vs (C,D), Court 2: (E,F) vs (G,H)
  - All 8 players play in round 1

### Constraints
- **Minimum players**: `n_courts * 4` players required
- **No round conflicts**: A player cannot appear in multiple matches of the same round
- **Match count**: Automatically adjusted to be a multiple of `n_courts`
- **Cut points**: Only evaluated at round boundaries

## 🧬 Chromosome Representation

### Match Structure
Each match consists of two teams:
- Format: `(A,B) vs (C,D)`
- Example: `(A,D) vs (B,C)`

### Chromosome Encoding
A chromosome represents a complete calendar (list of matches).

**Proposed encoding:**
- Matrix of size `(N, match_representation)`
  - `N` = total number of matches to play (multiple of n_courts)
  - `match_representation` = one-hot encoding vector representing players in a match

**Example with 4 players (A,B,C,D):**
- Match (A,B) vs (C,D) → `[1,1,0,0, 0,0,1,1]`
  - First 4 bits: team 1 (A,B)
  - Next 4 bits: team 2 (C,D)

**Example with 7 players (A,B,C,D,E,F,G):**
- Match (A,D) vs (B,C) → `[1,0,0,1,0,0,0, 0,1,1,0,0,0,0]`
  - First 7 bits: team 1 (A,D)
  - Next 7 bits: team 2 (B,C)

**Complete chromosome for N=3 matches:**
```
[
  [1,1,0,0,0,0,0, 0,0,1,1,0,0,0],  # Match 1: (A,B) vs (C,D)
  [1,0,0,1,0,0,0, 0,1,0,0,1,0,0],  # Match 2: (A,D) vs (B,E)
  [0,0,1,0,1,0,0, 0,0,0,1,0,1,0]   # Match 3: (C,E) vs (D,F)
]
```

**Validation requirements:**
- Each match must have exactly 4 different players
- Each team must have exactly 2 players
- No player can appear in both teams of the same match

## 📊 Fitness Function (Heuristics)

The fitness evaluates the quality of a calendar based on 7 main criteria (6 penalties + 1 bonus):

### 0. **Valid Match Constraint** (Hard Constraint)
- **Objective:** Every match must have exactly 4 different players
- **Validation:** Each match vector must have exactly 4 ones (2 in each team)
- **Penalty:** INFINITE penalty if a match has repeated players or invalid structure
- **Note:** This is a hard constraint that must always be satisfied

### 0.1. **Round Conflict Constraint** (Hard Constraint - Multiple Courts)
- **Objective:** A player cannot appear in multiple matches within the same round
- **Validation:** For each round, check that no player appears more than once
- **Penalty:** INFINITE penalty if any round has player conflicts
- **Note:** Only applies when `n_courts > 1`. Ensures simultaneous play is physically possible.
- **Example:** With 2 courts, if player A is in both matches of round 1, the calendar is INVALID

### 1. **Balance of Matches per Player** (HIGH PRIORITY)
- **Objective:** All players should play a similar number of matches
- **Penalty:** Strong if the difference between players > 1
- **Metric:** Standard deviation or max-min difference
- **Weight:** This is the MOST IMPORTANT criterion (highest weight)
- **Formula:** `penalty = (max_matches - min_matches)^2`

### 2. **Opponent Repetition**
- **Objective:** Minimize players facing each other repeatedly
- **Penalty:** Proportional to the number of times they face each other
- **Metric:** Sum of opponent pair repetitions
- **Formula:** `penalty = sum((repetitions - 1)^2 for each opponent pair)`

### 3. **Team Repetition**
- **Objective:** Minimize players playing together repeatedly
- **Penalty:** Strong if a team repeats too many times
- **Metric:** Quadratic sum of team repetitions
- **Formula:** `penalty = sum((repetitions - 1)^2 for each team pair)`

### 4. **Player Waiting Rounds**
- **Objective:** Minimize the number of consecutive rounds a player waits without playing
- **Penalty:** Penalize long waiting periods between rounds for each player
- **Metric:** Sum of waiting rounds for all players
- **Note:** With multiple courts, waiting is measured in ROUNDS, not individual matches
- **Formula:** `penalty = sum(waiting_rounds^2 for each player)`
- **Example (n_courts=1):** If player A plays match 1, then waits matches 2,3,4, then plays match 5, they waited 3 rounds
- **Example (n_courts=2):** If player A plays in round 1, skips round 2, plays round 3, they waited 1 round

### 5. **Early Cut Points Bonus** (IMPORTANT)
- **Objective:** Incentivize calendars that have cut points as early as possible
- **Bonus:** Reward solutions where the first cut point appears early in the calendar
- **Rationale:** It's better to have a usable tournament after 10 matches than after 30
- **Formula:** `bonus = 1000.0 / (first_perfect_cut_index + 1) + additional_bonuses`
- **Note:** This is a POSITIVE contribution to fitness (bonus, not penalty)
- **Example:** First perfect cut at match 7 is much better than at match 28

### Fitness Formula
```python
fitness = -(
    w0 * penalty_invalid_matches +      # Infinite if invalid
    w1 * penalty_balance +               # HIGHEST weight
    w2 * penalty_opponent_repetition +
    w3 * penalty_team_repetition +
    w4 * penalty_waiting_rounds
) + w5 * bonus_early_cuts                # POSITIVE bonus
```

**Recommended weights:**
- `w0 = float('inf')` (hard constraint)
- `w1 = 100.0` (very high - most important)
- `w2 = 10.0` (medium)
- `w3 = 10.0` (medium)
- `w4 = 5.0` (low-medium)
- `w5 = 50.0` (high - encourage early cut points)

## 🔍 Cut Points

### Definition
A cut point is a position in the calendar where the tournament can be finished while maintaining balance.

**IMPORTANT:** The earlier a cut point appears, the better. A tournament that can be stopped after fewer rounds is more flexible.

### Multiple Courts Consideration
With multiple courts (`n_courts > 1`), cut points are ONLY evaluated at **round boundaries**:
- It doesn't make sense to stop mid-round where some courts have played and others haven't
- Cut point positions are expressed as ROUND NUMBERS, not match indices
- Example: With 2 courts, a cut at "round 5" means after match 10

### Types of Cuts

**Perfect Cut:**
- Maximum difference in matches between players = 0
- All players have played exactly the same number of matches
- **Example (n_courts=2):** After round 4 (8 matches), all 8 players have played 4 matches each
- **Ideal:** First perfect cut should appear in the first 30% of rounds

**Acceptable Cut:**
- Maximum difference in matches between players ≤ 1
- Almost all players have played the same number of matches
- **Example:** After round 6, some played 5 and others 6
- **Minimum requirement:** At least one cut point should exist before 60% of rounds

### Detection
After generating the calendar, iterate through each round boundary and calculate:
```python
# Only check at round boundaries
for round_num in range(1, total_rounds + 1):
    cut_index = round_num * n_courts  # Last match of the round
    matches_per_player = count_matches_until(cut_index)
    max_difference = max(matches_per_player) - min(matches_per_player)
    
    if max_difference == 0:
        perfect_cuts.append(round_num)
    elif max_difference <= 1:
        acceptable_cuts.append(round_num)
```

### Quality Criteria
- **Excellent:** First perfect cut in first 30% of matches
- **Good:** First perfect cut in first 50% of matches
- **Acceptable:** First acceptable cut in first 60% of matches
- **Poor:** No cut points until after 60% of matches (solution rejected)

## 🧪 Genetic Algorithm

### Configurable Parameters
```python
N_PLAYERS = 8            # Number of players
N_ROUNDS = 10            # Number of rounds to play
N_COURTS = 2             # Number of courts (1 = sequential, 2+ = simultaneous rounds)
                         # Total matches = N_ROUNDS × N_COURTS
POPULATION_SIZE = 100    # Population size
GENERATIONS = 200        # Number of generations
MUTATION_RATE = 0.1      # Mutation probability
CROSSOVER_RATE = 0.8     # Crossover probability
ELITISM_SIZE = 2         # Number of best individuals to keep
```

### Multiple Courts Requirements
- Minimum players: `N_COURTS * 4`
- Total matches = `N_ROUNDS × N_COURTS`
- Example: 10 rounds with 2 courts = 20 matches total
- Example: 8 players with 2 courts = all 8 can play simultaneously each round

### Genetic Operators

**1. Initialization:**
- Generate initial population of random valid calendars
- Each calendar has N_MATCHES matches
- Each match must have exactly 4 different players
- Matrix representation: `(N_MATCHES, 2 * N_PLAYERS)`

**2. Selection:**
- Tournament selection (binary or k-tournament)
- Roulette wheel selection
- Select individuals with better fitness for reproduction

**3. Crossover:**
- Single-point, two-point, or uniform crossover
- Exchange segments of calendars between parents
- **Important:** Validate that resulting matches are valid (4 different players)
- If invalid matches are created, repair them or regenerate

**4. Mutation:**
Possible operations:
- Swap two players within a match (keeping teams valid)
- Swap the order of two matches in the calendar
- Replace a complete match with a random valid one
- Swap players between two different matches
- **Important:** Always maintain the constraint of 4 different players per match

**5. Replacement:**
- Elitism: keep the best individuals from previous generation
- Replace the rest with new generation
- Ensures the best solution never gets worse

### Algorithm Flow
```
1. Initialize random population
2. For each generation:
   a. Evaluate fitness of all individuals
   b. Select parents
   c. Apply crossover
   d. Apply mutation
   e. Create new generation (with elitism)
   f. Track best fitness
3. Return best individual found
```

## 📤 Program Output

### Output Format (Single Court)
```
=== AMERICAN TOURNAMENT CALENDAR ===
Players: A, B, C, D, E, F, G
Total matches: 50

Match 1: (A,D) vs (B,C)
Match 2: (A,E) vs (D,F)
...

=== CUT POINTS ===
Perfect cuts: [7, 14, 21, 35]
Acceptable cuts: [10, 18, 25, 32, 40, 48]
```

### Output Format (Multiple Courts)
```
=== AMERICAN TOURNAMENT CALENDAR ===
Players: A, B, C, D, E, F, G, H
Courts: 2 | Total Rounds: 10 | Total Matches: 20

📅 Round 1:
  🎾 Court 1 - Match 1: (A,B) vs (C,D)
  🎾 Court 2 - Match 2: (E,F) vs (G,H)

📅 Round 2:
  🎾 Court 1 - Match 3: (A,E) vs (B,F)
  🎾 Court 2 - Match 4: (C,G) vs (D,H)
...

=== CUT POINTS ===
Perfect cuts (rounds): [1, 2, 5, 10]  -- Round boundaries only
Acceptable cuts (rounds): [3, 4, 6, 7, 8, 9]
```

### CSV Export Format (Multiple Courts)
```csv
Round,Court,Match #,Team 1,Team 2,Perfect Cut,Acceptable Cut
1,1,1,A,B,C,D,,
1,2,2,E,F,G,H,✓,✓
2,1,3,A,E,B,F,,
2,2,4,C,G,D,H,✓,✓
```

## 🏗️ Project Structure

The project is organized into multiple files for better modularity:

```
american-tenis-tournament/
├── src/
│   ├── genetic_algorithm.py    # GA logic and classes
│   └── printer.py              # Output formatting
├── docs_agent/
│   ├── agent.md                # This file - project overview
│   └── implementation.md       # Implementation details and tasks
├── main.py                     # Main execution script
├── tournament.ipynb            # Jupyter notebook for easy execution
└── README.md
```

For detailed implementation information, class structures, and task tracking, see [`implementation.md`](./implementation.md).

## 🔧 Possible Extensions

### Future Improvements
1. **Additional Constraints:**
   - Avoid a player playing consecutive matches
   - Assign courts/schedules
   - Consider skill levels for balanced matches

2. **Optimizations:**
   - Parallelize fitness calculation
   - Hybrid algorithms (GA + local search)
   - Alternative chromosome representations

3. **Interface:**
   - GUI to configure parameters
   - Export calendar to CSV/PDF
   - Graphical visualization of balance

4. **Analysis:**
   - Fitness evolution graphs
   - Repetition statistics
   - Comparison of different configurations

## 📝 Implementation Notes

### Important Considerations

1. **Match Validation:**
   - Each match must have exactly 4 different players
   - No player can be repeated in the same match
   - This is a HARD CONSTRAINT that must always be satisfied

2. **Number of Players vs Match Size:**
   - Each match requires exactly 4 players (2 teams of 2)
   - With 7 players, 4 play and 3 wait in each match
   - With 8 players, 4 play and 4 wait in each match
   - The fitness function should minimize waiting rounds for all players

3. **Sequential Match Concept:**
   - Matches are played one at a time (sequentially)
   - A player waits if they don't play in consecutive matches
   - Example: Player A plays match 1, waits matches 2-4, plays match 5 → waited 3 rounds

4. **Fitness Balance:**
   - Penalty weights should be adjusted experimentally
   - Prioritize match balance per player (highest weight)
   - Waiting rounds should be minimized
   - Repetitions are less critical in long calendars

5. **Matrix Representation:**
   - Calendar shape: `(N_MATCHES, 2 * N_PLAYERS)`
   - Each row is a match
   - First N_PLAYERS bits: team 1
   - Next N_PLAYERS bits: team 2
   - Exactly 4 ones per row (2 per team)

## 🚀 How to Run

### Option 1: Using main.py (Command Line)

```bash
# Run with default values
python main.py

# Modify parameters by editing main.py:
# - N_PLAYERS = 7
# - N_MATCHES = 50
# - GENERATIONS = 200
```

### Option 2: Using Jupyter Notebook (Interactive)

```bash
# Start Jupyter
jupyter notebook

# Open tournament.ipynb
# Run cells interactively
# Modify parameters in the notebook cells
```

The notebook provides a more comfortable and interactive way to:
- Experiment with different parameters
- Visualize results
- Run multiple configurations
- Save and compare different runs

## 📚 References

- **Genetic Algorithms:** Optimization technique inspired by natural evolution
- **American Tournament:** Format where everyone plays against everyone in different combinations
- **Scheduling Problem:** Variant of the resource assignment problem

---

**Creation Date:** 2025-11-29  
**Version:** 1.0  
**Author:** AI System for sports calendar generation

