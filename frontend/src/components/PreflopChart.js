import React, { useState, useEffect } from "react";
import "./PreflopChart.css";

const API_URL = process.env.REACT_APP_API_URL || "/api";

const TIER_COLORS = {
  premium: { bg: "#1a3d2e", border: "#2d6a4f", color: "#52c77e" },
  strong: { bg: "#2a3d1e", border: "#5a8a3a", color: "#8bc34a" },
  playable: { bg: "#3d3520", border: "#b8860b", color: "#daa520" },
  marginal: { bg: "#3d2a1c", border: "#8b5e3c", color: "#cd853f" },
  trash: { bg: "#2a2a2a", border: "#4a4a4a", color: "#777" },
};

function PreflopChart() {
  const [chart, setChart] = useState(null);
  const [ranks, setRanks] = useState([]);
  const [hoveredCell, setHoveredCell] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/preflop-chart`)
      .then((r) => r.json())
      .then((data) => {
        setChart(data.chart);
        setRanks(data.ranks);
      })
      .catch(() => {});
  }, []);

  if (!chart) return <div className="preflop-chart loading">Loading chart...</div>;

  return (
    <div className="preflop-chart">
      <h3>Pre-Flop Starting Hand Chart</h3>
      <p className="chart-sub">Sklansky-Malmuth groupings. Hover to see details.</p>

      <div className="chart-legend">
        {Object.entries(TIER_COLORS).map(([tier, colors]) => (
          <span key={tier} className="legend-item" style={{ color: colors.color }}>
            <span className="legend-dot" style={{ background: colors.color }} />
            {tier.charAt(0).toUpperCase() + tier.slice(1)}
          </span>
        ))}
      </div>

      <div className="chart-grid">
        <div className="chart-row header-row">
          <div className="chart-cell corner"></div>
          {ranks.map((r) => (
            <div key={r} className="chart-cell col-header">{r}</div>
          ))}
        </div>
        {chart.map((row, i) => (
          <div key={i} className="chart-row">
            <div className="chart-cell row-header">{ranks[i]}</div>
            {row.map((cell, j) => {
              const colors = TIER_COLORS[cell.tier];
              return (
                <div
                  key={j}
                  className={`chart-cell hand-cell ${hoveredCell === cell.name ? "hovered" : ""}`}
                  style={{
                    background: colors.bg,
                    borderColor: colors.border,
                    color: colors.color,
                  }}
                  onMouseEnter={() => setHoveredCell(cell.name)}
                  onMouseLeave={() => setHoveredCell(null)}
                  title={`${cell.name} — Group ${cell.group} (${cell.tier})`}
                >
                  <span className="cell-name">{cell.name}</span>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {hoveredCell && (
        <div className="chart-tooltip">
          {hoveredCell}
        </div>
      )}
    </div>
  );
}

export default PreflopChart;
