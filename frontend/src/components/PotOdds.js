import React, { useState } from "react";
import "./PotOdds.css";

const API_URL = process.env.REACT_APP_API_URL || "/api";

function PotOdds() {
  const [potSize, setPotSize] = useState("");
  const [betToCall, setBetToCall] = useState("");
  const [outs, setOuts] = useState("");
  const [cardsToCome, setCardsToCome] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleCalculate = async () => {
    setError(null);
    setResult(null);

    const pot = parseFloat(potSize);
    const bet = parseFloat(betToCall);
    const outsNum = parseInt(outs) || 0;

    if (isNaN(pot) || pot <= 0) {
      setError("Enter a valid pot size");
      return;
    }
    if (isNaN(bet) || bet <= 0) {
      setError("Enter a valid bet to call");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/pot-odds`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pot_size: pot,
          bet_to_call: bet,
          total_outs: outsNum,
          cards_to_come: cardsToCome,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Calculation failed");
      }

      setResult(await response.json());
    } catch (err) {
      setError(err.message);
    }
  };

  const isPositiveEV = result?.decision?.includes("Profitable");

  return (
    <div className="pot-odds">
      <h3>Pot Odds Calculator</h3>
      <p className="pot-odds-sub">Determine if a call is profitable</p>

      <div className="pot-odds-inputs">
        <div className="pot-input-group">
          <label>Pot Size</label>
          <input
            type="number"
            placeholder="100"
            value={potSize}
            onChange={(e) => setPotSize(e.target.value)}
          />
        </div>
        <div className="pot-input-group">
          <label>Bet to Call</label>
          <input
            type="number"
            placeholder="25"
            value={betToCall}
            onChange={(e) => setBetToCall(e.target.value)}
          />
        </div>
        <div className="pot-input-group">
          <label>Outs</label>
          <input
            type="number"
            placeholder="9"
            value={outs}
            onChange={(e) => setOuts(e.target.value)}
          />
        </div>
        <div className="pot-input-group">
          <label>Cards to Come</label>
          <div className="cards-toggle">
            <button
              className={cardsToCome === 1 ? "active" : ""}
              onClick={() => setCardsToCome(1)}
            >
              1
            </button>
            <button
              className={cardsToCome === 2 ? "active" : ""}
              onClick={() => setCardsToCome(2)}
            >
              2
            </button>
          </div>
        </div>
      </div>

      <button className="pot-calc-btn" onClick={handleCalculate}>
        Calculate Pot Odds
      </button>

      {error && <div className="pot-error">{error}</div>}

      {result && (
        <div className="pot-results">
          <div className="pot-result-grid">
            <div className="pot-stat">
              <span className="pot-stat-label">Pot Odds</span>
              <span className="pot-stat-value">{result.pot_odds_pct}%</span>
              <span className="pot-stat-sub">{result.pot_odds_ratio}</span>
            </div>
            <div className="pot-stat">
              <span className="pot-stat-label">Hand Odds</span>
              <span className="pot-stat-value">{result.hand_odds_pct}%</span>
              <span className="pot-stat-sub">{result.required_pot_ratio}</span>
            </div>
            <div className="pot-stat">
              <span className="pot-stat-label">Breakeven</span>
              <span className="pot-stat-value">{result.breakeven_equity}%</span>
            </div>
            <div className="pot-stat">
              <span className="pot-stat-label">EV / Call</span>
              <span className={`pot-stat-value ${result.ev_per_call >= 0 ? "positive" : "negative"}`}>
                {result.ev_per_call >= 0 ? "+" : ""}{result.ev_per_call}
              </span>
            </div>
          </div>
          <div className={`pot-decision ${isPositiveEV ? "profitable" : "unprofitable"}`}>
            {result.decision}
          </div>
        </div>
      )}
    </div>
  );
}

export default PotOdds;
