# Texas Hold'em Equity Calculator

A full-featured Texas Hold'em equity calculator powered by Monte Carlo simulation. Built with a Python/FastAPI backend supporting multi-core parallel processing and a React frontend with interactive card selection, community board support, hand category breakdowns, pre-flop strategy charts, pot odds analysis, raise sizing recommendations, advanced pro-level strategy engine, and calculation history.

---

## Table of Contents

- [Features](#features)
- [How Monte Carlo Simulation Works](#how-monte-carlo-simulation-works)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Running Locally](#running-locally)
- [API Reference](#api-reference)
- [Frontend Components](#frontend-components)
- [Hand Evaluation Algorithm](#hand-evaluation-algorithm)
- [Pro Strategy Engine](#pro-strategy-engine)
- [Raise Sizing Logic](#raise-sizing-logic)
- [Performance](#performance)
- [Recommendation Logic](#recommendation-logic)
- [Sklansky-Malmuth Hand Rankings](#sklansky-malmuth-hand-rankings)
- [Tech Stack](#tech-stack)

---

## Features

- **Monte Carlo equity calculation** — Estimate win/tie/loss probabilities for any hole card combo against 1–9 opponents using 50,000 randomized simulations
- **Community card support** — Run simulations at any street: pre-flop, flop (3 cards), turn (4 cards), or river (5 cards)
- **Multi-core parallelization** — Distributes simulation workload across all CPU cores via a persistent `ProcessPoolExecutor` with async integration
- **Royal Flush recognition** — Distinguishes Royal Flush (ace-high straight flush) from regular straight flushes as its own hand category
- **Hand category breakdown** — See how often your hand makes each category (High Card through Royal Flush) across all simulations
- **Pre-flop starting hand chart** — Interactive 13×13 grid with Sklansky-Malmuth group rankings and color-coded tiers
- **Pot odds calculator** — Input pot size, bet-to-call, outs, and cards-to-come for pot odds %, hand odds %, breakeven equity, EV per call, and profitable/unprofitable decision
- **Outs calculator** — Automatic detection of flush draws, straight draws, overcards, and set draws with drawing probabilities
- **Raise sizing advisor** — Input your stack size and pot size to receive equity-based raise amounts, pot percentages, SPR analysis, and remaining stack calculations
- **Pro strategy engine** — Advanced recommendations including check-raises, slow-plays, semi-bluffs, traps, floats, block bets, overbets, double barrels, and psychological tips based on equity, street, hand distribution, and opponent count
- **Calculation history** — Tracks past calculations in localStorage with one-click replay
- **Sub-2s API response** — 50,000 simulations complete in under 2 seconds with parallel processing

---

## How Monte Carlo Simulation Works

The Monte Carlo method estimates probabilities by running many random trials and counting outcomes. For poker equity:

1. **Remove known cards** — The hero's hole cards (and any community cards already dealt) are removed from the 52-card deck.

2. **Deal remaining community cards** — If the board is incomplete, random cards are drawn to fill it to 5 community cards.

3. **Deal opponent hole cards** — Each opponent receives 2 random cards from the remaining deck.

4. **Evaluate all 7-card hands** — Every player's best hand is evaluated directly from their 2 hole cards + 5 community cards using a pure-Python 7-card evaluator (no need to enumerate all 21 five-card combinations).

5. **Compare and tally** — The hero's hand score is compared against all opponents. A win, tie, or loss is recorded for that trial.

6. **Repeat 50,000 times** — Steps 2–5 repeat for 50,000 simulations. The win/tie/loss counts divided by N give the probability estimates.

### Statistical Accuracy

The **Law of Large Numbers** guarantees convergence to true values. Standard error for a binary outcome with probability p over N trials:

$$SE = \sqrt{\frac{p(1-p)}{N}}$$

At 50,000 simulations with p ≈ 0.5, the standard error is ±0.22%.

### Parallelization Strategy

The simulation workload is split into chunks across all available CPU cores:

1. A persistent `ProcessPoolExecutor` is created at module load (avoids per-request pool creation overhead)
2. Each worker receives its own RNG seed for reproducibility
3. Workers run independent batches of `run_simulation()` in parallel
4. Results (wins, ties, losses, hand category counts) are aggregated in the main process
5. Integration with FastAPI uses `asyncio.run_in_executor()` for non-blocking request handling

This approach avoids the ~0.7s overhead of creating/destroying a process pool per request and achieves near-linear speedup with core count.

---

## Architecture

```
┌─────────────────┐     HTTP/JSON     ┌──────────────────┐
│   React Frontend │ ◄──────────────► │  FastAPI Backend  │
│   (port 3000)    │                  │   (port 8000)     │
└─────────────────┘                   ├──────────────────┤
                                      │  routes.py        │ ← Request validation, endpoint logic
                                      │  parallel.py      │ ← Persistent ProcessPoolExecutor
                                      │  simulation.py    │ ← Monte Carlo engine + eval_7()
                                      │  analysis.py      │ ← Outs, pot odds, strategy, raise sizing
                                      └──────────────────┘
                                             │
                                      ┌──────┴──────┐
                                      │  CPU Core 1  │
                                      │  CPU Core 2  │
                                      │  CPU Core N  │
                                      └─────────────┘
```

---

## Project Structure

```
MonteCarlo/
├── backend/
│   ├── main.py              # FastAPI app with CORS, uvicorn entry point
│   ├── routes.py            # 6 API endpoints with Pydantic validation
│   ├── simulation.py        # Core Monte Carlo engine, eval_7() hand evaluator
│   ├── parallel.py          # Persistent ProcessPoolExecutor + async bridge
│   ├── analysis.py          # Outs, pot odds, hand classification, Sklansky groups,
│   │                        #   raise sizing, advanced strategy engine
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.js         # React entry point
│       ├── App.js           # Main app with tab navigation & state management
│       ├── App.css           # Global styles, tab nav, layout
│       └── components/
│           ├── CardPicker.js    # Hole card selection grid (rank × suit)
│           ├── CardPicker.css
│           ├── BoardPicker.js   # Community card selector (flop/turn/river)
│           ├── BoardPicker.css
│           ├── Results.js       # Equity results, raise sizing, pro strategy display
│           ├── Results.css
│           ├── HandBreakdown.js # Horizontal bar chart of hand category distribution
│           ├── HandBreakdown.css
│           ├── PotOdds.js       # Pot odds calculator with EV analysis
│           ├── PotOdds.css
│           ├── PreflopChart.js  # 13×13 pre-flop starting hand chart
│           ├── PreflopChart.css
│           ├── History.js       # Calculation history with localStorage persistence
│           └── History.css
├── .gitignore
└── README.md
```

---

## Running Locally

### Prerequisites

- Python 3.10+
- Node.js 16+
- npm

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API starts at `http://localhost:8000`. Interactive Swagger docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm start
```

Opens at `http://localhost:3000`.

---

## API Reference

### `POST /api/calculate`

Calculate equity using Monte Carlo simulation. Supports pre-flop through river. Optionally provide stack and pot sizes for raise sizing and strategy recommendations.

**Request:**

```json
{
  "hole_cards": ["As", "Kh"],
  "num_opponents": 3,
  "num_simulations": 50000,
  "community_cards": ["Td", "7s", "2c"],
  "stack_size": 500,
  "pot_size": 100
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hole_cards` | `string[]` | Yes | Exactly 2 cards. Format: rank + suit (e.g. `As`, `Td`, `2c`) |
| `num_opponents` | `int` | No | 1–9 (default: 1) |
| `num_simulations` | `int` | No | 1,000–500,000 (default: 50,000) |
| `community_cards` | `string[]` | No | 0, 3, 4, or 5 cards (default: []) |
| `stack_size` | `float` | No | Your current stack size in chips/dollars (default: 0) |
| `pot_size` | `float` | No | Current pot size in chips/dollars (default: 0) |

**Card format:** Two characters — rank (`2`–`9`, `T`, `J`, `Q`, `K`, `A`) + suit (`c`, `d`, `h`, `s`).

**Response:**

```json
{
  "hole_cards": ["AS", "KH"],
  "community_cards": ["TD", "7S", "2C"],
  "num_opponents": 3,
  "win_probability": 0.3412,
  "tie_probability": 0.0198,
  "loss_probability": 0.639,
  "equity": 0.3511,
  "total_simulations": 50000,
  "recommendation": "Fold",
  "hand_name": "AKo",
  "sklansky_group": 2,
  "preflop_tier": "Premium",
  "street": "Flop",
  "hand_category_breakdown": {
    "High Card": 0.4123,
    "One Pair": 0.3891,
    "Two Pair": 0.0821,
    "Three of a Kind": 0.0312,
    "Straight": 0.0187,
    "Flush": 0.0098,
    "Full House": 0.0052,
    "Four of a Kind": 0.0003,
    "Straight Flush": 0.0001,
    "Royal Flush": 0.0000
  },
  "raise_sizing": {
    "action": "check",
    "raise_amount": 0,
    "raise_pct_pot": 0,
    "spr_before": 5.0,
    "pot_after_raise": 100,
    "spr_after": 5.0,
    "remaining_stack": 500,
    "reasoning": "Equity too low (35.1%) — check or fold."
  },
  "strategy": {
    "primary_action": "check-fold",
    "primary_label": "Check / Fold",
    "primary_explanation": "With 35% equity against 3 opponents, this hand isn't strong enough to continue.",
    "advanced_plays": [],
    "strategic_tips": [
      "⚠️ Bluffing into multiple opponents is rarely profitable..."
    ]
  }
}
```

### `POST /api/outs`

Calculate drawing outs and probabilities for flop or turn.

**Request:**

```json
{
  "hole_cards": ["Ah", "Kh"],
  "community_cards": ["7h", "2h", "Tc"]
}
```

**Response:** Current hand classification, total outs, draw types detected (flush draw, straight draw, etc.), and hit probabilities for turn and river.

### `POST /api/pot-odds`

Calculate pot odds and expected value analysis.

**Request:**

```json
{
  "pot_size": 100,
  "bet_to_call": 20,
  "total_outs": 9,
  "cards_to_come": 2
}
```

**Response:**

```json
{
  "pot_odds_pct": 16.67,
  "hand_odds_pct": 35.0,
  "breakeven_equity": 16.67,
  "ev_per_call": 3.67,
  "decision": "profitable"
}
```

### `GET /api/preflop-chart`

Returns the complete 13×13 pre-flop starting hand chart with Sklansky-Malmuth groupings.

**Response:** A `chart` array (13 rows × 13 columns) where each cell contains `{name, group, tier}`, plus a `ranks` array of rank labels.

### `GET /api/hand-categories`

Returns the ordered list of hand categories (High Card through Royal Flush) with their indices.

### `GET /api/health`

Health check endpoint.

```json
{ "status": "ok", "version": "2.0.0" }
```

---

## Frontend Components

### Calculator Tab

The main equity calculation interface:

- **CardPicker** — Two visual rank×suit grids for selecting hole cards. Disabled cards (already selected elsewhere) are greyed out.
- **BoardPicker** — Five-slot community card selector labeled Flop / Turn / River. Opens a grid picker for card selection. Validates that the board is 0, 3, 4, or 5 cards.
- **Opponent Selector** — 1–9 toggle buttons for opponent count.
- **Stack & Pot Inputs** — Optional dollar inputs for your stack size and current pot size. When provided, enables raise sizing recommendations and SPR analysis.
- **Results** — Win/tie/loss probability bars, equity percentage, card rendering with suit symbols and colors, street badge, hand name, Sklansky group, and pre-flop tier label.
- **Raise Sizing** — When stack/pot are provided: recommended action (raise/check/all-in), raise amount, % of pot, SPR before and after, pot after raise, remaining stack, and reasoning.
- **Pro Strategy** — Advanced plays section with primary action (check-raise, slow-play, semi-bluff, etc.), detailed explanation, alternative plays with icons and "when to use" guidance, and psychological tips.
- **HandBreakdown** — Horizontal bar chart showing how often your hand makes each category (High Card through Royal Flush) with color-coded bars.

### Pre-Flop Chart Tab

Interactive 13×13 grid (169 cells) showing every starting hand combination:

- **Diagonal:** Pocket pairs (AA, KK, ..., 22)
- **Upper triangle:** Suited hands (AKs, AQs, ...)
- **Lower triangle:** Off-suit hands (AKo, AQo, ...)
- **Color-coded by tier:** Premium (green), Strong (lime), Playable (gold), Marginal (brown), Trash (gray)
- **Hover for details** with group number and tier label

### Pot Odds Tab

Dedicated pot odds and EV calculator:

- Input pot size, bet-to-call, number of outs, and cards-to-come (1 or 2)
- Displays pot odds %, hand odds %, breakeven equity, EV per call
- Color-coded profitable/unprofitable decision indicator

### History Tab

Scrollable list of past calculations:

- Displays hole cards, board, opponents, equity
- Color-coded equity: green (≥60%), gold (40–60%), red (<40%)
- Click any entry to load those inputs back into the calculator
- Persisted in localStorage (up to 50 entries)

---

## Hand Evaluation Algorithm

The hand evaluator (`eval_7()`) takes 7 cards and returns a comparable tuple `(category, *kickers)` without needing to enumerate all 21 five-card combinations. It works by:

1. **Counting ranks and suits** — Tally how many cards of each rank and each suit exist.
2. **Checking for flushes** — If any suit has ≥5 cards, extract those cards for straight-flush detection.
3. **Checking for straights** — Scan rank counts for 5+ consecutive ranks (with ace-low wrapping).
4. **Categorizing by count pattern:**
   - 4 of a kind → category 7
   - 3 + 2 (full house) → category 6
   - Flush → category 5
   - Straight → category 4
   - 3 of a kind → category 3
   - Two pair → category 2
   - One pair → category 1
   - High card → category 0

Categories (highest to lowest): Royal Flush (9 — ace-high straight flush), Straight Flush (8), Four of a Kind (7), Full House (6), Flush (5), Straight (4), Three of a Kind (3), Two Pair (2), One Pair (1), High Card (0).

The evaluator returns `(8, 12)` for a Royal Flush (straight flush with ace-high). The simulation and display layers map this to a distinct "Royal Flush" category separate from other straight flushes.

The tuple comparison (e.g., `(6, 10, 7)` for full house tens full of sevens) enables direct Python comparison: `hand_a > hand_b` correctly determines the winner.

---

## Pro Strategy Engine

The strategy engine (`get_advanced_strategy()` in `analysis.py`) goes beyond simple Raise/Call/Fold by analyzing multiple factors to recommend deceptive and advanced plays:

### Inputs Analyzed

- **Equity** — Win probability from simulation
- **Street** — Pre-flop, flop, turn, or river
- **Opponents** — Heads-up vs. multiway dynamics
- **Hand distribution** — How often your hand makes flushes, straights, draws, etc.
- **Stack-to-pot ratio (SPR)** — Deep vs. short stack play
- **Pre-flop tier** — Starting hand strength class

### Plays Recommended

| Play | When | Psychological Angle |
|------|------|---------------------|
| **Check-Raise** | Monster hand heads-up post-flop | Feign weakness to induce a bet, then strike |
| **Slow-Play / Trap** | Premium pre-flop, monster on dry boards | Let opponents build the pot; spring the trap later |
| **Limp-Reraise** | AA/KK vs. aggressive opponents | Disguise ultra-strength as weakness |
| **Semi-Bluff** | Drawing hands (flush/straight draws) with equity | Win now via fold equity OR improve if called |
| **Float** | Decent draws heads-up | Call one street, then take it away on the next |
| **Continuation Bluff** | Air on dry boards | Bet your perceived range, not your actual hand |
| **Double Barrel** | Bluff on flop + turn with scare cards | Two barrels of aggression tell a convincing strength story |
| **River Bluff** | Weak hand heads-up on river | Large bet representing a completed draw |
| **Block Bet** | Marginal hand, pot control | Small bet to prevent opponent from making a bigger bluff |
| **Overbet for Value** | Monster after showing weakness | Charge strong-but-second-best hands that feel pot-committed |
| **Probe Bet** | Marginal hand, information seeking | Small bet to test opponent strength cheaply |
| **Value Bet** | Strong hand multiway | Charge draws, protect your hand |

### Psychological Tips

The engine also provides contextual tips:

- **Balance your range** — Vary actions with similar hand strengths to stay unpredictable
- **The Hollywood pause** — Take extra time before check-raising to sell the deception
- **Read bet sizing** — Small bets = cheap showdown; overbets = polarized (nuts or bluff)
- **Adjust to opponents** — Bluff tight folders, value-bet calling stations
- **Commit or fold** — At low SPR, there's no room for clever play — get it in or give up
- **Don't bluff multiway** — Each extra opponent destroys fold equity

---

## Raise Sizing Logic

When stack size and pot size are provided, the calculator recommends optimal bet sizing:

| Equity | Action | Sizing |
|--------|--------|--------|
| ≥ 80% | All-in | Entire remaining stack |
| ≥ 55% | Raise | 60–100% of pot (scaled by equity) |
| 40–55% | Small bet | ~33% of pot (pot control) |
| < 40% | Check | No investment |

Additional factors:

- **SPR (Stack-to-Pot Ratio)** — Reported before and after the raise. Low SPR (< 3) suggests commit-or-fold dynamics.
- **Remaining stack** — Shows how much you'd have left after the recommended raise.
- **Reasoning** — Natural language explanation of why this sizing was chosen.

---

## Performance

| Metric | Value |
|--------|-------|
| Single-thread throughput | ~34,000 simulations/sec |
| 50k sims (parallel, 8 cores) | ~1.0 sec |
| API response (50k sims) | < 2 sec |
| Process pool startup | 0 sec (persistent) |

Performance depends on CPU core count and clock speed. The persistent process pool eliminates the ~0.7 second overhead of creating a new pool per request.

---

## Recommendation Logic

### Basic Recommendation

| Equity | Recommendation |
|--------|---------------|
| ≥ 55% | **Raise** |
| 40–55% | **Call** |
| < 40% | **Fold** |

Equity formula: $\text{equity} = P(\text{win}) + 0.5 \times P(\text{tie})$

### Advanced Strategy

The pro strategy engine overlays sophisticated play recommendations on top of the basic recommendation. See [Pro Strategy Engine](#pro-strategy-engine) for the full breakdown of deceptive plays, psychological tactics, and when to deploy them.

---

## Sklansky-Malmuth Hand Rankings

The pre-flop chart uses the Sklansky-Malmuth hand groupings from *Hold'em Poker for Advanced Players*:

| Group | Tier | Hands |
|-------|------|-------|
| 1 | Premium | AA, KK, QQ, JJ, AKs |
| 2 | Premium | TT, AQs, AJs, KQs, AKo |
| 3 | Strong | 99, JTs, QJs, KJs, ATs, AQo |
| 4 | Strong | 88, KTs, QTs, J9s, T9s, 98s, AJo, KQo |
| 5 | Playable | 77, 87s, Q9s, T8s, KJo, QJo, JTo, 76s, 97s, A9s–A2s |
| 6 | Playable | 66, 55, ATo, 86s, KTo, QTo, 54s, K9s, J8s, 75s, T7s |
| 7 | Marginal | 44, 33, 22, 65s, J9o, T9o, 98o, 64s, 53s, 85s, K8s–K2s |
| 8 | Marginal | 87o, 76o, Q8s–Q2s, J7s–J2s, T6s–T2s, 95s–92s, 84s–82s, 74s–72s, 63s, 62s, 52s, 43s, 42s, 32s |
| 9 | Trash | Everything else |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend framework | FastAPI 0.115.6 | Async REST API with auto-generated docs |
| ASGI server | Uvicorn 0.34.0 | High-performance async server |
| Validation | Pydantic 2.10.4 | Request/response models with field validators |
| Numerics | NumPy 2.2.1 | Array operations for deck shuffling and dealing |
| Parallelism | ProcessPoolExecutor | Multi-core simulation distribution |
| Async bridge | asyncio.run_in_executor | Non-blocking integration with FastAPI |
| Frontend | React 18 | Component-based UI |
| Build tool | react-scripts 5.0.1 | Development server and production builds |
| Storage | localStorage | Client-side calculation history persistence |
