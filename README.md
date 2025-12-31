# American Tournament Organizer (Tennis / Padel)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-178%20passing-brightgreen.svg)](tests/)
[![Code style: Clean](https://img.shields.io/badge/code%20style-clean-black.svg)](https://github.com/psf/black)

This project implements an automatic calendar generator for "Americano" style tournaments using **Genetic Algorithms**. It is designed for doubles sports like tennis, padel, or pickleball. Supports **multiple courts** for simultaneous matches.

## 🎾 What is this project?

In an "Americano" tournament, the goal is for **everyone to play with everyone** (and against everyone) as many times as possible, changing partners in every match. Managing this manually for groups of 7, 9, or 13 players is mathematically complex.

This tool generates optimized calendars that:
1. Minimize partner repetition.
2. Balance waiting times between matches.
3. Ensure everyone plays a similar number of matches.
4. Find ideal "cut points" to take breaks or finish the tournament.
5. **Support multiple courts** for simultaneous play.

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

To generate a calendar, simply run the main script:

```bash
# If using uv
uv run python main.py

# If using standard python
python main.py
```

### Configuration

You can adjust parameters directly in `main.py`:

```python
# Tournament parameters
N_PLAYERS = 8           # Number of players
N_ROUNDS = 10           # Number of rounds to play
N_COURTS = 2            # Number of courts (default: 1)
# Total matches = N_ROUNDS × N_COURTS

# GA parameters (optimized for maximum cut points)
POPULATION_SIZE = 200   # High diversity
MUTATION_RATE = 0.2     # Aggressive exploration
CROSSOVER_RATE = 0.8    # Standard recombination
GENERATIONS = 200       # With early stopping
```

### Multiple Courts 🎾🎾

With multiple courts, matches are grouped into **rounds** where `N_COURTS` matches are played simultaneously:

```
📅 Round 1:
  🎾 Court 1 - Match 1: (A,B) vs (C,D)
  🎾 Court 2 - Match 2: (E,F) vs (G,H)

📅 Round 2:
  🎾 Court 1 - Match 3: (A,E) vs (B,F)
  🎾 Court 2 - Match 4: (C,G) vs (D,H)
```

**Minimum players per court configuration:**
- 1 court: 4 players minimum
- 2 courts: 8 players minimum  
- N courts: 4×N players minimum

## 📤 Outputs & Results

After running the script, check the `outputs/` folder:

1. **`tournament_calendar.csv`**: The raw schedule with Round, Court, Match ID, Teams. Easy to import into Excel or Google Sheets.
2. **`tournament_results.txt`**: A human-readable report containing:
    * The match list grouped by rounds.
    * **Statistics per player**: How many matches they played, waiting time.
    * **Cut Points Analysis**: Specific rounds where you can stop the tournament.

### ✂️ What are "Cut Points"?

A **Cut Point** is a moment in the schedule where **every single player has played exactly the same number of matches**.

* **Why they matter:** In social tournaments, you often have limited time. If you stop at a random point, some players will have played more than others - unfair!
* **The Solution:** This algorithm optimizes the schedule to create these "safe harbors" early and often. You can aim for these points to take a break or finish the event fairly.

## 📂 Project Structure

```
american-tenis-tournament/
├── src/
│   ├── dataclasses.py              # Match and Calendar models
│   ├── genetic_algorithm.py        # GA logic and fitness functions
│   ├── printer.py                  # Output formatting
│   └── hyperparameter_optimizer.py # Optimization tools
├── tests/                          # 178 tests
├── docs_agent/                     # Technical documentation
├── outputs/                        # Results (.csv and .txt)
└── main.py                         # Main script
```

## 🧠 Algorithm & Hyperparameters

This solution uses a **Genetic Algorithm (GA)** optimized for combinatorial constraints.

**Selected Configuration (Optimized):**
* **Population Size:** `200` (High diversity)
* **Mutation Rate:** `0.20` (Aggressive exploration)
* **Crossover Rate:** `0.8` (Standard recombination)
* **Generations:** `200` with Early Stopping

**Key Optimization:**
The algorithm heavily penalizes **imbalanced matches** and rewards **early cut points**.

## 🧪 Testing

```bash
# Run all tests (178 tests)
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentation

Detailed technical documentation in `docs_agent/`:
- **agent.md**: Project overview and concepts
- **implementation.md**: Technical details
- **changelog.md**: Development history
- **tests_info.md**: Test documentation

## 📄 License

This project is licensed under the MIT License.

---

**Version**: 2.0  
**Last Updated**: 2025-12-31
