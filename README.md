# Texas Hold'em Equity Calculator

A web-based Texas Hold'em equity calculator powered by Monte Carlo simulation. Estimate win/tie/loss probabilities for any hole card combination against 1-9 opponents, with hand breakdowns, pre-flop strategy charts, pot odds analysis, raise sizing, and an advanced pro-level strategy engine.

**Live App:** [Deployed on Vercel](#) <!-- Replace # with your Vercel URL after deployment -->

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Using the App](#using-the-app)
- [Deployment](#deployment)
- [Running Locally](#running-locally)
- [API Reference](#api-reference)
- [Hand Evaluation Algorithm](#hand-evaluation-algorithm)
- [Pro Strategy Engine](#pro-strategy-engine)
- [Raise Sizing Logic](#raise-sizing-logic)
- [Recommendation Logic](#recommendation-logic)
- [Sklansky-Malmuth Hand Rankings](#sklansky-malmuth-hand-rankings)
- [Tech Stack](#tech-stack)

---

## Features

- **Monte Carlo equity calculation** — Estimate win/tie/loss probabilities for any hole card combo against 1-9 opponents using randomized simulations
- **Community card support** — Run simulations at any street: pre-flop, flop (3 cards), turn (4 cards), or river (5 cards)
- **Multi-core parallelization** — Distributes simulation workload across CPU cores locally; runs single-threaded in the serverless deployment for instant cold starts
- **Royal Flush recognition** — Distinguishes Royal Flush from regular straight flushes as its own hand category
- **Hand category breakdown** — See how often your hand makes each category (High Card through Royal Flush) across all simulations
- **Pre-flop starting hand chart** — Interactive 13x13 grid with Sklansky-Malmuth group rankings and color-coded tiers
- **Pot odds calculator** — Input pot size, bet-to-call, outs, and cards-to-come for pot odds %, hand odds %, breakeven equity, EV per call, and profitable/unprofitable decision
- **Outs calculator** — Automatic detection of flush draws, straight draws, overcards, and set draws with drawing probabilities
- **Raise sizing advisor** — Input your stack size and pot size to receive equity-based raise amounts, pot percentages, SPR analysis, and remaining stack calculations
- **Pro strategy engine** — Advanced recommendations including check-raises, slow-plays, semi-bluffs, traps, floats, block bets, overbets, double barrels, and psychological tips
- **Calculation history** — Tracks past calculations in your browser with one-click replay
- **Deployed on Vercel** — No installation required. Open the app and start calculating

---

## How It Works

The Monte Carlo method estimates probabilities by running many random trials and counting outcomes:

1. **Remove known cards** — Your hole cards (and any community cards already dealt) are removed from the 52-card deck
2. **Deal remaining community cards** — If the board is incomplete, random cards are drawn to fill it to 5
3. **Deal opponent hole cards** — Each opponent receives 2 random cards from the remaining deck
4. **Evaluate all 7-card hands** — Every player's best hand is evaluated from their 2 hole cards + 5 community cards using a pure-Python 7-card evaluator
5. **Compare and tally** — Your hand is compared against all opponents. A win, tie, or loss is recorded
6. **Repeat thousands of times** — The win/tie/loss counts divided by N give the probability estimates

### Statistical Accuracy

The **Law of Large Numbers** guarantees convergence to true values. Standard error for a binary outcome with probability p over N trials:

$$SE = \sqrt{\frac{p(1-p)}{N}}$$

At 50,000 simulations with p = 0.5, the standard error is +/-0.22%.

---

## Architecture

```
                  Vercel Edge Network
                         |
        +----------------+----------------+
        |                                 |
   Static Assets                   Python Serverless
   (React Build)                   Function (/api/*)
        |                                 |
   React Frontend              FastAPI Application
   - CardPicker               - routes.py (endpoints)
   - BoardPicker              - simulation.py (engine)
   - Results                  - analysis.py (strategy)
   - HandBreakdown            - parallel.py (execution)
   - PotOdds
   - PreflopChart
   - History
```

---

## Using the App

### Calculator Tab

1. **Select your hole cards** — Click the rank and suit grids to pick your two cards
2. **Set the board** (optional) — Add 3 (flop), 4 (turn), or 5 (river) community cards
3. **Choose opponents** — Select 1-9 opponents
4. **Enter stack & pot** (optional) — For raise sizing and SPR analysis
5. **Click "Calculate Equity"** — Results appear in under a few seconds

The results show:
- Win / tie / loss probability bars
- Equity percentage with recommendation (Raise / Call / Fold)
- Hand name, Sklansky group, and pre-flop tier
- Raise sizing (if stack/pot provided)
- Pro strategy recommendations with psychological tips
- Hand category breakdown chart

### Pre-Flop Chart Tab

Interactive 13x13 grid (169 cells) showing every starting hand combination:
- **Diagonal:** Pocket pairs (AA, KK, ..., 22)
- **Upper triangle:** Suited hands (AKs, AQs, ...)
- **Lower triangle:** Off-suit hands (AKo, AQo, ...)
- **Color-coded by tier:** Premium, Strong, Playable, Marginal, Trash
- **Hover for details** with group number and tier label

### Pot Odds Tab

Dedicated pot odds and EV calculator:
- Input pot size, bet-to-call, number of outs, and cards-to-come (1 or 2)
- Displays pot odds %, hand odds %, breakeven equity, EV per call
- Color-coded profitable/unprofitable decision indicator

### History Tab

Scrollable list of past calculations:
- Displays hole cards, board, opponents, equity
- Color-coded equity: green (>=60%), gold (40-60%), red (<40%)
- Click any entry to load those inputs back into the calculator
- Persisted in your browser's localStorage (up to 50 entries)

---

## Deployment

The app is deployed on **Vercel** as a monorepo with a React static frontend and Python serverless API functions.

### Deploy Your Own

1. Fork or clone this repository
2. Install the [Vercel CLI](https://vercel.com/docs/cli):
   ```bash
   npm i -g vercel
   ```
3. Deploy:
   ```bash
   vercel
   ```
4. For production:
   ```bash
   vercel --prod
   ```

Vercel automatically:
- Builds the React frontend (`frontend/build`)
- Deploys the Python API as a serverless function (`api/index.py`)
- Routes `/api/*` requests to the serverless function
- Serves all other routes from the static build

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `/api` | API base URL (only needed if hosting the API separately) |

---

## Running Locally

For local development, you can run the backend and frontend separately with full multi-core parallelization.

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
REACT_APP_API_URL=http://localhost:8000/api npm start
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
| `num_opponents` | `int` | No | 1-9 (default: 1) |
| `num_simulations` | `int` | No | 1,000-500,000 (default: 50,000) |
| `community_cards` | `string[]` | No | 0, 3, 4, or 5 cards (default: []) |
| `stack_size` | `float` | No | Your current stack size in chips/dollars (default: 0) |
| `pot_size` | `float` | No | Current pot size in chips/dollars (default: 0) |

**Card format:** Two characters — rank (`2`-`9`, `T`, `J`, `Q`, `K`, `A`) + suit (`c`, `d`, `h`, `s`).

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
  "hand_category_breakdown": { "High Card": 0.4123, "...": "..." },
  "raise_sizing": { "action": "check", "raise_amount": 0, "...": "..." },
  "strategy": { "primary_action": "check-fold", "...": "..." }
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

Returns the complete 13x13 pre-flop starting hand chart with Sklansky-Malmuth groupings.

### `GET /api/hand-categories`

Returns the ordered list of hand categories (High Card through Royal Flush) with their indices.

### `GET /api/health`

Health check endpoint.

---

## Hand Evaluation Algorithm

The hand evaluator (`eval_7()`) takes 7 cards and returns a comparable tuple `(category, *kickers)` without enumerating all 21 five-card combinations:

1. **Count ranks and suits** — Tally how many cards of each rank and each suit exist
2. **Check for flushes** — If any suit has >=5 cards, extract those for straight-flush detection
3. **Check for straights** — Scan rank counts for 5+ consecutive ranks (with ace-low wrapping)
4. **Categorize by count pattern** — Four of a kind, full house, flush, straight, trips, two pair, pair, high card

Categories (highest to lowest): Royal Flush (9), Straight Flush (8), Four of a Kind (7), Full House (6), Flush (5), Straight (4), Three of a Kind (3), Two Pair (2), One Pair (1), High Card (0).

---

## Pro Strategy Engine

The strategy engine analyzes equity, street, opponent count, hand distribution, SPR, and pre-flop tier to recommend advanced plays:

| Play | When | Psychological Angle |
|------|------|---------------------|
| **Check-Raise** | Monster hand heads-up post-flop | Feign weakness to induce a bet, then strike |
| **Slow-Play / Trap** | Premium pre-flop, monster on dry boards | Let opponents build the pot; spring the trap later |
| **Limp-Reraise** | AA/KK vs. aggressive opponents | Disguise ultra-strength as weakness |
| **Semi-Bluff** | Drawing hands with equity | Win now via fold equity OR improve if called |
| **Float** | Decent draws heads-up | Call one street, take it away on the next |
| **Continuation Bluff** | Air on dry boards | Bet your perceived range, not your actual hand |
| **Double Barrel** | Bluff on flop + turn with scare cards | Two barrels of aggression tell a convincing story |
| **River Bluff** | Weak hand heads-up on river | Large bet representing a completed draw |
| **Block Bet** | Marginal hand, pot control | Small bet to prevent a bigger bluff |
| **Overbet for Value** | Monster after showing weakness | Charge pot-committed second-best hands |
| **Probe Bet** | Marginal hand, information seeking | Small bet to test opponent strength cheaply |
| **Value Bet** | Strong hand multiway | Charge draws, protect your hand |

---

## Raise Sizing Logic

When stack size and pot size are provided, the calculator recommends optimal bet sizing:

| Equity | Action | Sizing |
|--------|--------|--------|
| >= 80% | All-in | Entire remaining stack |
| >= 55% | Raise | 60-100% of pot (scaled by equity) |
| 40-55% | Small bet | ~33% of pot (pot control) |
| < 40% | Check | No investment |

Additional factors: SPR (Stack-to-Pot Ratio), remaining stack, and natural language reasoning.

---

## Recommendation Logic

| Equity | Recommendation |
|--------|---------------|
| >= 55% | **Raise** |
| 40-55% | **Call** |
| < 40% | **Fold** |

Equity formula: equity = P(win) + 0.5 * P(tie)

The pro strategy engine overlays sophisticated play recommendations on top of the basic recommendation. See [Pro Strategy Engine](#pro-strategy-engine) for the full breakdown.

---

## Sklansky-Malmuth Hand Rankings

| Group | Tier | Hands |
|-------|------|-------|
| 1 | Premium | AA, KK, QQ, JJ, AKs |
| 2 | Premium | TT, AQs, AJs, KQs, AKo |
| 3 | Strong | 99, JTs, QJs, KJs, ATs, AQo |
| 4 | Strong | 88, KTs, QTs, J9s, T9s, 98s, AJo, KQo |
| 5 | Playable | 77, 87s, Q9s, T8s, KJo, QJo, JTo, 76s, 97s, A9s-A2s |
| 6 | Playable | 66, 55, ATo, 86s, KTo, QTo, 54s, K9s, J8s, 75s, T7s |
| 7 | Marginal | 44, 33, 22, 65s, J9o, T9o, 98o, 64s, 53s, 85s, K8s-K2s |
| 8 | Marginal | 87o, 76o, Q8s-Q2s, J7s-J2s, T6s-T2s, 95s-92s, 84s-82s, 74s-72s, 63s, 62s, 52s, 43s, 42s, 32s |
| 9 | Trash | Everything else |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Hosting | Vercel | Static assets + Python serverless functions |
| Backend framework | FastAPI 0.115.6 | Async REST API with auto-generated docs |
| Validation | Pydantic 2.10.4 | Request/response models with field validators |
| Numerics | NumPy 2.2.1 | Array operations for deck shuffling and dealing |
| Parallelism | ProcessPoolExecutor | Multi-core simulation (local) / single-threaded (serverless) |
| Frontend | React 18 | Component-based UI |
| Build tool | react-scripts 5.0.1 | Development server and production builds |
| Storage | localStorage | Client-side calculation history persistence |
