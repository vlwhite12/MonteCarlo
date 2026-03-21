import React, { useState, useCallback } from "react";
import CardPicker from "./components/CardPicker";
import BoardPicker from "./components/BoardPicker";
import Results from "./components/Results";
import HandBreakdown from "./components/HandBreakdown";
import PotOdds from "./components/PotOdds";
import PreflopChart from "./components/PreflopChart";
import History from "./components/History";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "/api";

const TABS = [
  { id: "calculator", label: "Calculator" },
  { id: "preflop", label: "Pre-Flop Chart" },
  { id: "potodds", label: "Pot Odds" },
  { id: "history", label: "History" },
];

function App() {
  const [activeTab, setActiveTab] = useState("calculator");
  const [card1, setCard1] = useState(null);
  const [card2, setCard2] = useState(null);
  const [boardCards, setBoardCards] = useState([]);
  const [numOpponents, setNumOpponents] = useState(1);
  const [stackSize, setStackSize] = useState("");
  const [potSize, setPotSize] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("pokerHistory") || "[]");
    } catch {
      return [];
    }
  });

  const allSelected = [card1, card2, ...boardCards].filter(Boolean);

  const handleCalculate = async () => {
    if (!card1 || !card2) {
      setError("Please select both hole cards.");
      return;
    }
    if (card1 === card2) {
      setError("Please select two different cards.");
      return;
    }
    // Board must be 0, 3, 4, or 5 cards
    if (![0, 3, 4, 5].includes(boardCards.length)) {
      setError("Board must have 0 (pre-flop), 3 (flop), 4 (turn), or 5 (river) cards.");
      return;
    }

    setError(null);
    setLoading(true);
    setResults(null);

    try {
      const response = await fetch(`${API_URL}/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hole_cards: [card1, card2],
          num_opponents: numOpponents,
          num_simulations: 50000,
          community_cards: boardCards,
          stack_size: parseFloat(stackSize) || 0,
          pot_size: parseFloat(potSize) || 0,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Calculation failed");
      }

      const data = await response.json();
      setResults(data);

      // Add to history
      const entry = {
        hole_cards: [card1, card2],
        community_cards: boardCards,
        num_opponents: numOpponents,
        num_simulations: 50000,
        equity: data.equity,
        recommendation: data.recommendation,
        hand_name: data.hand_name,
        preflop_tier: data.preflop_tier,
        timestamp: Date.now(),
      };
      const updated = [entry, ...history].slice(0, 50);
      setHistory(updated);
      localStorage.setItem("pokerHistory", JSON.stringify(updated));
    } catch (err) {
      setError(err.message || "Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = useCallback((entry) => {
    setCard1(entry.hole_cards[0]);
    setCard2(entry.hole_cards[1]);
    setBoardCards(entry.community_cards || []);
    setNumOpponents(entry.num_opponents);
    setActiveTab("calculator");
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Texas Hold'em Equity Calculator</h1>
        <p className="subtitle">Monte Carlo Simulation Engine &middot; Multi-Core Parallel Processing</p>
      </header>

      <nav className="tab-nav">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === "calculator" && (
          <>
            <section className="input-section">
              <div className="card-selection">
                <h2>Select Your Hole Cards</h2>
                <div className="card-pickers">
                  <div className="picker-group">
                    <label>Card 1</label>
                    <CardPicker
                      value={card1}
                      onChange={setCard1}
                      disabledCards={allSelected}
                    />
                  </div>
                  <div className="picker-group">
                    <label>Card 2</label>
                    <CardPicker
                      value={card2}
                      onChange={setCard2}
                      disabledCards={allSelected}
                    />
                  </div>
                </div>
              </div>

              <BoardPicker
                cards={boardCards}
                onChange={setBoardCards}
                disabledCards={allSelected}
              />

              <div className="opponents-section">
                <label htmlFor="opponents">Number of Opponents</label>
                <div className="opponent-selector">
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
                    <button
                      key={n}
                      className={`opp-btn ${numOpponents === n ? "active" : ""}`}
                      onClick={() => setNumOpponents(n)}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              <div className="sizing-inputs">
                <h2>Stack &amp; Pot (optional)</h2>
                <p className="sizing-hint">Enter values to get raise sizing recommendations</p>
                <div className="sizing-row">
                  <div className="sizing-field">
                    <label>Your Stack</label>
                    <div className="input-wrap">
                      <span className="input-prefix">$</span>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        placeholder="e.g. 200"
                        value={stackSize}
                        onChange={(e) => setStackSize(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="sizing-field">
                    <label>Current Pot</label>
                    <div className="input-wrap">
                      <span className="input-prefix">$</span>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        placeholder="e.g. 30"
                        value={potSize}
                        onChange={(e) => setPotSize(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <button
                className="calculate-btn"
                onClick={handleCalculate}
                disabled={loading || !card1 || !card2}
              >
                {loading ? "Calculating..." : "Calculate Equity"}
              </button>

              {error && <div className="error">{error}</div>}
            </section>

            {results && (
              <>
                <section className="results-section">
                  <Results data={results} />
                </section>

                {results.hand_category_breakdown && (
                  <section className="breakdown-section">
                    <HandBreakdown breakdown={results.hand_category_breakdown} />
                  </section>
                )}
              </>
            )}
          </>
        )}

        {activeTab === "preflop" && (
          <section className="tab-content">
            <PreflopChart />
          </section>
        )}

        {activeTab === "potodds" && (
          <section className="tab-content">
            <PotOdds />
          </section>
        )}

        {activeTab === "history" && (
          <section className="tab-content">
            <History history={history} onSelect={handleHistorySelect} />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>Built with FastAPI &amp; React &middot; Monte Carlo Simulation &middot; Multi-Process Parallelization</p>
      </footer>
    </div>
  );
}

export default App;
