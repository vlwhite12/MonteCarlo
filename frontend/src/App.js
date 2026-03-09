import React, { useState } from "react";
import CardPicker from "./components/CardPicker";
import Results from "./components/Results";
import "./App.css";

const API_URL = "http://localhost:8000/api";

function App() {
  const [card1, setCard1] = useState(null);
  const [card2, setCard2] = useState(null);
  const [numOpponents, setNumOpponents] = useState(1);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCalculate = async () => {
    if (!card1 || !card2) {
      setError("Please select both hole cards.");
      return;
    }
    if (card1 === card2) {
      setError("Please select two different cards.");
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
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Calculation failed");
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message || "Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  const selectedCards = [card1, card2].filter(Boolean);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Texas Hold'em Equity Calculator</h1>
        <p className="subtitle">Monte Carlo Simulation Engine</p>
      </header>

      <main className="app-main">
        <section className="input-section">
          <div className="card-selection">
            <h2>Select Your Hole Cards</h2>
            <div className="card-pickers">
              <div className="picker-group">
                <label>Card 1</label>
                <CardPicker
                  value={card1}
                  onChange={setCard1}
                  disabledCards={selectedCards}
                />
              </div>
              <div className="picker-group">
                <label>Card 2</label>
                <CardPicker
                  value={card2}
                  onChange={setCard2}
                  disabledCards={selectedCards}
                />
              </div>
            </div>
          </div>

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
          <section className="results-section">
            <Results data={results} />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
