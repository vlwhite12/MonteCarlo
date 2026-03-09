# Texas Hold'em Equity Calculator

A Monte Carlo simulation engine that calculates pre-flop win probabilities for Texas Hold'em poker hands. Built with Python/FastAPI on the backend and React on the frontend.

## How the Monte Carlo Method Works

The Monte Carlo method estimates probabilities by running many random simulations and tallying the outcomes.

For Texas Hold'em equity:

1. **Deal random community cards** — The simulator randomly selects 5 community cards (flop, turn, river) from the remaining deck.
2. **Deal opponent hole cards** — Each opponent receives 2 random cards from the remaining deck.
3. **Evaluate all hands** — Every player's best 5-card hand is determined from their 2 hole cards + 5 community cards using combinatorial evaluation over all 21 possible 5-card selections.
4. **Compare and tally** — The hero's hand is compared against all opponents. A win, tie, or loss is recorded.
5. **Repeat thousands of times** — Steps 1–4 are repeated (default: 50,000 times) and the win/tie/loss counts produce the probability estimates.

The **Law of Large Numbers** guarantees that as the number of simulations increases, the estimated probabilities converge to the true values. At 50,000 simulations the standard error is roughly ±0.2%.

### Parallelization

The simulation workload is split evenly across all available CPU cores using Python's `multiprocessing.Pool`. Each worker runs an independent batch of simulations with its own RNG seed, and the results are aggregated. This cuts total runtime by ~50–80% depending on core count.

## Project Structure

```
MonteCarlo/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── routes.py            # API route definitions
│   ├── simulation.py        # Core Monte Carlo simulation engine (NumPy)
│   ├── parallel.py          # Multiprocessing handler
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js           # Main React component
│       ├── App.css
│       ├── index.js
│       └── components/
│           ├── CardPicker.js # Visual card selection grid
│           ├── CardPicker.css
│           ├── Results.js    # Results display with bars
│           └── Results.css
└── README.md
```

## Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API server starts at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm start
```

Opens at `http://localhost:3000`.

## API Usage

### `POST /api/calculate`

Calculate equity for a given hand.

**Request body:**

```json
{
  "hole_cards": ["As", "Kh"],
  "num_opponents": 3,
  "num_simulations": 50000
}
```

**Card format:** Two characters — rank (`2-9`, `T`, `J`, `Q`, `K`, `A`) + suit (`c`, `d`, `h`, `s`).

**Response:**

```json
{
  "hole_cards": ["AS", "KH"],
  "num_opponents": 3,
  "win_probability": 0.3412,
  "tie_probability": 0.0198,
  "loss_probability": 0.639,
  "equity": 0.3511,
  "total_simulations": 50000,
  "recommendation": "Fold"
}
```

### `GET /api/health`

Health check.

```json
{ "status": "ok" }
```

## Recommendation Logic

| Equity | Action |
| --- | --- |
| ≥ 55% | **Raise** |
| 40–55% | **Call** |
| < 40% | **Fold** |

Equity = win probability + (tie probability × 0.5)

## Stack

- **Backend:** Python 3.11+, NumPy, multiprocessing, FastAPI, Uvicorn
- **Frontend:** React 18
