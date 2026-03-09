import React from "react";
import "./HandBreakdown.css";

const CATEGORIES = [
  "Straight Flush", "Four of a Kind", "Full House", "Flush",
  "Straight", "Three of a Kind", "Two Pair", "One Pair", "High Card"
];

const COLORS = {
  "Straight Flush": "#ffd700",
  "Four of a Kind": "#e6a817",
  "Full House": "#c084fc",
  "Flush": "#60a5fa",
  "Straight": "#34d399",
  "Three of a Kind": "#f87171",
  "Two Pair": "#fb923c",
  "One Pair": "#a3a3a3",
  "High Card": "#6b7280",
};

function HandBreakdown({ breakdown }) {
  if (!breakdown) return null;

  // Sort by category strength (display strongest first)
  const entries = CATEGORIES
    .map((name) => ({ name, pct: (breakdown[name] || 0) * 100 }))
    .filter((e) => e.pct > 0.05);

  if (entries.length === 0) return null;

  const maxPct = Math.max(...entries.map((e) => e.pct));

  return (
    <div className="hand-breakdown">
      <h3>Hand Category Distribution</h3>
      <p className="breakdown-sub">How often your hand makes each category</p>
      <div className="breakdown-bars">
        {entries.map((e) => (
          <div className="breakdown-row" key={e.name}>
            <span className="breakdown-label">{e.name}</span>
            <div className="breakdown-track">
              <div
                className="breakdown-fill"
                style={{
                  width: `${(e.pct / maxPct) * 100}%`,
                  background: COLORS[e.name] || "#666",
                }}
              />
            </div>
            <span className="breakdown-value">{e.pct.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HandBreakdown;
