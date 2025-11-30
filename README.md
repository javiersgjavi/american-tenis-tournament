# American Tournament Organizer (Tennis / Padel)

This project implements an automatic calendar generator for "Americano" style tournaments using **Genetic Algorithms**. It is designed for doubles sports like tennis, padel, or pickleball.

## 🎾 What is this project?

In an "Americano" tournament, the goal is for **everyone to play with everyone** (and against everyone) as many times as possible, changing partners in every match. Managing this manually for groups of 7, 9, or 13 players is mathematically complex.

This tool generates optimized calendars that:
1.  Minimize partner repetition.
2.  Balance waiting times between matches.
3.  Ensure everyone plays a similar number of matches.
4.  Find ideal "cut points" to take breaks or finish the tournament.

## 🚀 Installation

The project uses modern Python. You can install it using `uv` (recommended) or `pip`.

### Option A: Using uv (Fast & Secure)
```bash
# Clone the repository
git clone <repo-url>
cd american-tenis-tournament

# Sync dependencies
uv sync
```

### Option B: Standard pip
```bash
pip install .
```

## 💻 Usage

To generate a calendar, simply run the main script. By default, it is configured for a standard scenario (e.g., 7 players).

```bash
# If using uv
uv run main.py

# If using standard python
python main.py
```

### Configuration
You can adjust parameters directly in `main.py`:
- `N_PLAYERS`: Total number of participants.
- `N_MATCHES`: Number of matches to generate.
- `WEIGHT_*`: Weights to prioritize balance vs. opponent variety.

## 📤 Outputs & Results

After running the script, check the `outputs/` folder:

1.  **`tournament_calendar.csv`**: The raw schedule. Columns: Match ID, Team 1, Team 2. Easy to import into Excel or Google Sheets.
2.  **`tournament_results.txt`**: A human-readable report containing:
    *   The match list.
    *   **Statistics per player**: How many matches they played, how long they waited.
    *   **Cut Points Analysis**: Specific matches where you can stop the tournament.

### ✂️ What are "Cut Points"?

A **Cut Point** is a magic moment in the schedule where **every single player has played exactly the same number of matches**.

*   **Why they matter:** In social tournaments, you often have limited time (e.g., 2 hours). If you run out of time at match #17, but Player A has played 6 games and Player B has played 4, people will be unhappy.
*   **The Solution:** This algorithm specifically optimizes the schedule to create these "safe harbors" early and often (e.g., at match 14, 21, 28). You can aim for these points to take a break or finish the event fairly.

## 📂 Project Structure

- `src/`: Source code for the genetic algorithm and data models.
- `outputs/`: Results are saved here (.csv and .txt).
- `docs_agent/`: Detailed technical documentation for developers or AI agents.
- `optimization_results/`: Hyperparameter optimization logs.

## 🧠 Algorithm & Hyperparameters

This solution uses a **Genetic Algorithm (GA)** optimized for combinatorial constraints. It evolves a population of calendars to minimize a cost function based on social and mathematical rules.

**Selected Configuration (Optimized):**
*   **Algorithm Type:** Generational GA with Elitism and Tournament Selection.
*   **Population Size:** `200` (High diversity).
*   **Mutation Rate:** `0.20` (Aggressive exploration to escape local optima).
*   **Crossover Rate:** `0.8` (Standard recombination).
*   **Generations:** `200` with Early Stopping.

**Key Optimization:**
The algorithm heavily penalizes **imbalanced matches** (everyone must play the same amount) and rewards **early cut points** (allowing the tournament to be comfortably stopped at multiple points).
