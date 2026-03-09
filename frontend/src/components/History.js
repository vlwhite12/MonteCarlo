import React from "react";
import "./History.css";

function History({ history, onSelect }) {
  if (!history || history.length === 0) {
    return (
      <div className="history-panel">
        <h3>Calculation History</h3>
        <p className="history-empty">No calculations yet. Run a simulation to get started.</p>
      </div>
    );
  }

  const formatCards = (cards) => {
    const SUITS = ["♣", "♦", "♥", "♠"];
    const RANKS = ["2","3","4","5","6","7","8","9","T","J","Q","K","A"];
    return cards.map((c) => RANKS[c >> 2] + SUITS[c & 3]).join(" ");
  };

  return (
    <div className="history-panel">
      <h3>Calculation History</h3>
      <div className="history-list">
        {history.map((entry, i) => {
          const eqPct = (entry.equity * 100).toFixed(1);
          const eqClass =
            entry.equity >= 0.6
              ? "equity-high"
              : entry.equity >= 0.4
              ? "equity-mid"
              : "equity-low";
          return (
            <div
              key={i}
              className="history-item"
              onClick={() => onSelect && onSelect(entry)}
            >
              <div className="history-hand">
                <span className="history-cards">{formatCards(entry.hole_cards)}</span>
                {entry.community_cards && entry.community_cards.length > 0 && (
                  <span className="history-board">
                    Board: {formatCards(entry.community_cards)}
                  </span>
                )}
              </div>
              <div className="history-meta">
                <span className="history-opponents">{entry.num_opponents} opp</span>
                <span className="history-sims">{(entry.num_simulations / 1000).toFixed(0)}k sims</span>
                <span className={`history-equity ${eqClass}`}>{eqPct}%</span>
              </div>
              {entry.hand_name && (
                <div className="history-detail">
                  <span className="history-hand-name">{entry.hand_name}</span>
                  {entry.preflop_tier && (
                    <span className={`history-tier tier-${entry.preflop_tier}`}>
                      {entry.preflop_tier}
                    </span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default History;
