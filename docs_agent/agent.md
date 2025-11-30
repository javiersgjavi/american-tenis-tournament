# Project Context: American Tournament Generator

This document serves as the source of truth and context for AI Agents (LLMs) working on this repository. It defines both the business logic (rules of American tennis/padel) and the technical implementation (genetic algorithm).

## 🎾 Domain Context (Business Logic)

### What is an "American Tournament"?
It is a popular social competition format in racquet sports (Tennis, Padel, Pickleball) designed for individual groups where **fixed partners do not exist**.

**Fundamental Rules:**
1.  **Individuality:** Players register individually, not as pairs.
2.  **Dynamic Rotation:** In every match, a player changes their partner and opponents.
3.  **Social Objective:** The goal is to maximize the "mix". A player should play with and against as many different people as possible.
4.  **Scoring:** Although played in pairs (2 vs 2), points are added to each player's individual ranking.
5.  **Physical Constraint:** In a group of $N$ players with $C$ available courts, only $C \times 4$ people can play simultaneously. The rest must wait.

### The Mathematical Problem
Organizing this manually is extremely difficult because several objectives conflict:
*   No one should wait too long on the bench.
*   Partners should not repeat (A and B shouldn't play together 3 times in a row).
*   Opponents should not repeat.
*   By the end of the tournament, everyone must have played the same number of matches.

This project solves this combinatorial optimization problem (NP-Hard) using Genetic Algorithms.

---

## 🧬 Technical Implementation: Genetic Algorithm

### Chromosome Representation
An "individual" in our population is a **Complete Calendar** (an ordered sequence of matches).

*   **Structure:** Matrix of `(N_MATCHES, 2 * N_PLAYERS)`.
*   **Encoding:** One-hot encoding per match.
    *   Example (7 players): `[1,0,1,0,0,0,0,  0,1,0,0,0,1,0]`
    *   Means: (P1, P3) vs (P2, P6).
    *   The first $N$ bits are Team 1, the next $N$ bits are Team 2.

### Fitness Function (Tournament "Quality")
The evaluation function (`fitness`) is a weighted sum of penalties (which we want to minimize) and bonuses.

#### Penalties (Things to avoid):
1.  **Match Imbalance (`w1` - Critical):** If Player A plays 10 matches and Player B plays 6, the tournament is a failure.
2.  **Opponent Repetition (`w2`):** Boring if you always play against the same people.
3.  **Teammate Repetition (`w3`):** Boring if you always play with the same partner.
4.  **Long Waits (`w4`):** If a player plays match 1 and then has to wait until match 10, they will get cold and bored. We seek a uniform distribution of breaks.

#### Bonuses (Things to seek):
1.  **Early Cut Points (`w5` - Strategic):**
    *   A "Cut Point" is a moment in the schedule where all players have played exactly the same number of matches.
    *   **Why it matters:** Allows organizers to take logistical breaks (eat, drink, switch sides) or end the tournament if rental time runs out, without anyone feeling cheated for having played less.

---

## 🏗️ Code Structure

*   **`src/genetic_algorithm.py`**: The core. Contains the `GeneticAlgorithm` class and evolution logic.
*   **`src/dataclasses.py`**: Type definitions (`Match`, `Calendar`). Uses Pydantic for strict validation ensuring valid matches (4 unique players).
*   **`src/utils.py`**: Mathematical helper functions.
*   **`main.py`**: Entry point. Configures hyperparameters and launches execution.

## 🔍 Key Parameters (Hyperparameters)

Based on optimization performed (`optimization_results/`), the recommended values for a standard tournament (7-13 players) are:

| Parameter | Rec. Value | Reason |
|-----------|------------|-------|
| `POPULATION_SIZE` | 100-200 | Sufficient diversity without being slow. |
| `MUTATION_RATE` | **0.20** | A high value is needed here to escape local minima and find perfect cut points. |
| `CROSSOVER_RATE` | 0.8 | Standard recombination. |
| `ELITISM` | 2-3 | Always preserve the best solutions found. |

## 🚀 Agent Guide (Maintenance Instructions)

If you need to modify the code, keep in mind:
1.  **Hard Validation:** Never allow an invalid match to be generated (e.g., a player playing against themselves or teams of 3). The `Match` class in `dataclasses.py` must be inviolable.
2.  **Performance:** Fitness evaluation runs thousands of times. Any change in `calculate_fitness` must be vectorized (NumPy) if possible.
3.  **Usability:** The end user is a tournament organizer, not a programmer. Outputs (`outputs/tournament_results.txt`) must be human-readable (names or letters A-Z, not 0-6 indices).

---
**Final Note:** This system prioritizes **fairness** over pure combination perfection. It is better to repeat a partner once than to leave a player waiting for 5 matches in a row.
