import React, { useState } from "react";
import "./BoardPicker.css";

const RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"];
const SUITS = [
  { code: "s", symbol: "♠", color: "#e0e0e0" },
  { code: "h", symbol: "♥", color: "#e74c3c" },
  { code: "d", symbol: "♦", color: "#3498db" },
  { code: "c", symbol: "♣", color: "#2ecc71" },
];

function BoardPicker({ cards, onChange, disabledCards, maxCards = 5 }) {
  const [open, setOpen] = useState(false);

  const handleSelect = (card) => {
    if (cards.includes(card)) {
      onChange(cards.filter((c) => c !== card));
    } else if (cards.length < maxCards) {
      const next = [...cards, card];
      // Only allow 0, 3, 4, or 5 for display, but allow building up
      onChange(next);
    }
  };

  const handleClear = () => {
    onChange([]);
  };

  const displayCard = (cardStr) => {
    const rank = cardStr[0];
    const suitObj = SUITS.find((s) => s.code === cardStr[1].toLowerCase());
    return (
      <span className="board-card" key={cardStr}>
        <span className="board-rank">{rank}</span>
        <span className="board-suit" style={{ color: suitObj?.color }}>
          {suitObj?.symbol}
        </span>
      </span>
    );
  };

  const streetLabel = () => {
    switch (cards.length) {
      case 0: return "Pre-Flop";
      case 1: return "1 card (need 3 for flop)";
      case 2: return "2 cards (need 3 for flop)";
      case 3: return "Flop";
      case 4: return "Turn";
      case 5: return "River";
      default: return "";
    }
  };

  return (
    <div className="board-picker">
      <div className="board-header">
        <h3>Community Cards <span className="street-badge">{streetLabel()}</span></h3>
        {cards.length > 0 && (
          <button className="clear-btn" onClick={handleClear}>Clear</button>
        )}
      </div>

      <div className="board-slots">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`board-slot ${i < cards.length ? "filled" : ""} ${i < 3 ? "flop" : i === 3 ? "turn" : "river"}`}
          >
            {i < cards.length ? displayCard(cards[i]) : (
              <span className="slot-label">
                {i < 3 ? "Flop" : i === 3 ? "Turn" : "River"}
              </span>
            )}
          </div>
        ))}
      </div>

      <button
        className="board-toggle"
        onClick={() => setOpen(!open)}
      >
        {open ? "Close Card Selector" : "Edit Board Cards"}
      </button>

      {open && (
        <div className="board-dropdown">
          <div className="board-grid">
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
                  const isOtherDisabled = disabledCards.includes(card) && !cards.includes(card);
                  const isOnBoard = cards.includes(card);
                  return (
                    <button
                      key={card}
                      className={`grid-cell card-cell ${isOnBoard ? "on-board" : ""} ${isOtherDisabled ? "disabled" : ""}`}
                      disabled={isOtherDisabled || (cards.length >= maxCards && !isOnBoard)}
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

export default BoardPicker;
