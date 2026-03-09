import React, { useState } from "react";
import "./CardPicker.css";

const RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"];
const SUITS = [
  { code: "s", symbol: "♠", color: "#e0e0e0" },
  { code: "h", symbol: "♥", color: "#e74c3c" },
  { code: "d", symbol: "♦", color: "#3498db" },
  { code: "c", symbol: "♣", color: "#2ecc71" },
];

function CardPicker({ value, onChange, disabledCards }) {
  const [open, setOpen] = useState(false);

  const handleSelect = (card) => {
    onChange(card);
    setOpen(false);
  };

  const displayCard = (cardStr) => {
    if (!cardStr) return null;
    const rank = cardStr[0];
    const suitObj = SUITS.find((s) => s.code === cardStr[1].toLowerCase());
    return (
      <span className="card-display">
        <span className="card-rank">{rank}</span>
        <span className="card-suit" style={{ color: suitObj?.color }}>
          {suitObj?.symbol}
        </span>
      </span>
    );
  };

  return (
    <div className="card-picker">
      <button
        className={`picker-button ${value ? "has-value" : ""}`}
        onClick={() => setOpen(!open)}
      >
        {value ? displayCard(value) : "Pick a card"}
      </button>

      {open && (
        <div className="picker-dropdown">
          <div className="picker-grid">
            <div className="grid-header">
              <div className="grid-cell corner"></div>
              {SUITS.map((s) => (
                <div key={s.code} className="grid-cell suit-header" style={{ color: s.color }}>
                  {s.symbol}
                </div>
              ))}
            </div>
            {RANKS.map((rank) => (
              <div key={rank} className="grid-row">
                <div className="grid-cell rank-header">{rank}</div>
                {SUITS.map((suit) => {
                  const card = rank + suit.code;
                  const isDisabled =
                    disabledCards.includes(card) && card !== value;
                  const isSelected = card === value;
                  return (
                    <button
                      key={card}
                      className={`grid-cell card-cell ${isSelected ? "selected" : ""} ${isDisabled ? "disabled" : ""}`}
                      disabled={isDisabled}
                      onClick={() => handleSelect(card)}
                      style={{ color: suit.color }}
                    >
                      {suit.symbol}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CardPicker;
