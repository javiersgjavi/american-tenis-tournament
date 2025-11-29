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

## 🧬 Chromosome Representation

### Match Structure
Each match consists of two teams:
- Format: `(A,B) vs (C,D)`
- Example: `(A,D) vs (B,C)`

### Chromosome Encoding
A chromosome represents a complete calendar (list of matches).

**Proposed encoding:**
- Matrix of size `(N, match_representation)`
  - `N` = total number of matches to play
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

The fitness evaluates the quality of a calendar based on 6 main criteria (5 penalties + 1 bonus):

### 0. **Valid Match Constraint** (Hard Constraint)
- **Objective:** Every match must have exactly 4 different players
- **Validation:** Each match vector must have exactly 4 ones (2 in each team)
- **Penalty:** INFINITE penalty if a match has repeated players or invalid structure
- **Note:** This is a hard constraint that must always be satisfied

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
- **Objective:** Minimize the number of consecutive matches a player waits without playing
- **Penalty:** Penalize long waiting periods between matches for each player
- **Metric:** Sum of waiting rounds for all players
- **Note:** Matches are played sequentially (one at a time)
- **Formula:** `penalty = sum(waiting_rounds^2 for each player)`
- **Example:** If player A plays match 1, then waits matches 2,3,4, then plays match 5, they waited 3 rounds

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
A cut point is an index in the calendar where the tournament can be finished while maintaining balance.

**IMPORTANT:** The earlier a cut point appears, the better. A tournament that can be stopped after 10 matches is more flexible than one requiring 30 matches.

### Types of Cuts

**Perfect Cut:**
- Maximum difference in matches between players = 0
- All players have played exactly the same number of matches
- **Example:** After match 8, all players have played 4 matches
- **Ideal:** First perfect cut should appear in the first 30% of the calendar

**Acceptable Cut:**
- Maximum difference in matches between players ≤ 1
- Almost all players have played the same number of matches
- **Example:** After match 12, some played 5 and others 6
- **Minimum requirement:** At least one cut point should exist before 60% of the calendar

### Detection
After generating the calendar, iterate through each index and calculate:
```python
matches_per_player = count_matches_until(index)
max_difference = max(matches_per_player) - min(matches_per_player)

if max_difference == 0:
    perfect_cuts.append(index)
elif max_difference <= 1:
    acceptable_cuts.append(index)
```

### Quality Criteria
- **Excellent:** First perfect cut in first 30% of matches
- **Good:** First perfect cut in first 50% of matches
- **Acceptable:** First acceptable cut in first 60% of matches
- **Poor:** No cut points until after 60% of matches (solution rejected)

## 🧪 Genetic Algorithm

### Configurable Parameters
```python
N_PLAYERS = 7            # Number of players
N_MATCHES = 50           # Matches to generate
POPULATION_SIZE = 100    # Population size
GENERATIONS = 200        # Number of generations
MUTATION_RATE = 0.1      # Mutation probability
CROSSOVER_RATE = 0.8     # Crossover probability
ELITISM_SIZE = 2         # Number of best individuals to keep
```

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

### Output Format
```
=== AMERICAN TOURNAMENT CALENDAR ===
Players: A, B, C, D, E, F, G
Total matches: 50

Match 1: (A,D) vs (B,C)
Match 2: (A,E) vs (D,F)
Match 3: (B,G) vs (C,E)
...
Match 50: (A,F) vs (C,G)

=== STATISTICS ===
Matches per player:
  A: 28 matches
  B: 29 matches
  C: 28 matches
  D: 29 matches
  E: 28 matches
  F: 28 matches
  G: 30 matches

=== CUT POINTS ===
Perfect cuts: [7, 14, 21, 35]
Acceptable cuts: [10, 18, 25, 32, 40, 48]
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

