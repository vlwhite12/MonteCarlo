import React from "react";
import "./Results.css";

function Results({ data }) {
  const { win_probability, tie_probability, loss_probability, equity, recommendation, total_simulations, hole_cards } = data;

  const recClass = recommendation.toLowerCase();

  return (
    <div className="results">
      <h2>Results</h2>

      <div className="hand-label">
        Hand: {hole_cards[0]} {hole_cards[1]} &nbsp;|&nbsp; {total_simulations.toLocaleString()} simulations
      </div>

      <div className="prob-bars">
        <div className="prob-row">
          <span className="prob-label">Win</span>
          <div className="bar-track">
            <div
              className="bar-fill bar-win"
              style={{ width: `${win_probability * 100}%` }}
            />
          </div>
          <span className="prob-value">{(win_probability * 100).toFixed(1)}%</span>
        </div>

        <div className="prob-row">
          <span className="prob-label">Tie</span>
          <div className="bar-track">
            <div
              className="bar-fill bar-tie"
              style={{ width: `${tie_probability * 100}%` }}
            />
          </div>
          <span className="prob-value">{(tie_probability * 100).toFixed(1)}%</span>
        </div>

        <div className="prob-row">
          <span className="prob-label">Loss</span>
          <div className="bar-track">
            <div
              className="bar-fill bar-loss"
              style={{ width: `${loss_probability * 100}%` }}
            />
          </div>
          <span className="prob-value">{(loss_probability * 100).toFixed(1)}%</span>
        </div>
      </div>

      <div className="equity-row">
        <span>Equity</span>
        <span className="equity-value">{(equity * 100).toFixed(1)}%</span>
      </div>

      <div className={`recommendation ${recClass}`}>
        <span className="rec-label">Recommendation</span>
        <span className="rec-value">{recommendation}</span>
      </div>
    </div>
  );
}

export default Results;
