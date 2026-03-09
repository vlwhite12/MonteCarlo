import React from "react";
import "./Results.css";

const SUITS = { s: "♠", h: "♥", d: "♦", c: "♣" };
const SUIT_COLORS = { s: "#e0e0e0", h: "#e74c3c", d: "#3498db", c: "#2ecc71" };

function renderCard(cardStr) {
  const rank = cardStr[0];
  const suit = cardStr[1].toLowerCase();
  return (
    <span className="res-card" key={cardStr}>
      <span className="res-rank">{rank}</span>
      <span className="res-suit" style={{ color: SUIT_COLORS[suit] }}>{SUITS[suit]}</span>
    </span>
  );
}

function Results({ data }) {
  const {
    win_probability, tie_probability, loss_probability,
    equity, recommendation, total_simulations,
    hole_cards, community_cards, num_opponents,
    hand_name, sklansky_group, preflop_tier, street,
    raise_sizing,
    strategy,
  } = data;

  const recClass = recommendation.toLowerCase();

  return (
    <div className="results">
      <h2>Results</h2>

      <div className="result-meta">
        <div className="meta-left">
          <div className="meta-hand">
            {hole_cards.map((c) => renderCard(c))}
            {community_cards && community_cards.length > 0 && (
              <>
                <span className="meta-divider">|</span>
                {community_cards.map((c) => renderCard(c))}
              </>
            )}
          </div>
          <span className="meta-info">
            {total_simulations.toLocaleString()} sims &middot; {num_opponents} opponent{num_opponents > 1 ? "s" : ""}
          </span>
        </div>
        <div className="meta-right">
          <span className="street-label">{street}</span>
        </div>
      </div>

      {hand_name && (
        <div className="hand-info-row">
          <span className="hand-name-tag">{hand_name}</span>
          {sklansky_group && (
            <span className="sklansky-tag">Group {sklansky_group}</span>
          )}
          {preflop_tier && (
            <span className={`tier-tag tier-${preflop_tier}`}>{preflop_tier}</span>
          )}
        </div>
      )}

      <div className="prob-bars">
        <div className="prob-row">
          <span className="prob-label">Win</span>
          <div className="bar-track">
            <div className="bar-fill bar-win" style={{ width: `${win_probability * 100}%` }} />
          </div>
          <span className="prob-value">{(win_probability * 100).toFixed(1)}%</span>
        </div>

        <div className="prob-row">
          <span className="prob-label">Tie</span>
          <div className="bar-track">
            <div className="bar-fill bar-tie" style={{ width: `${tie_probability * 100}%` }} />
          </div>
          <span className="prob-value">{(tie_probability * 100).toFixed(1)}%</span>
        </div>

        <div className="prob-row">
          <span className="prob-label">Loss</span>
          <div className="bar-track">
            <div className="bar-fill bar-loss" style={{ width: `${loss_probability * 100}%` }} />
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

      {raise_sizing && (
        <div className="raise-sizing">
          <h3>Raise Sizing</h3>
          <div className="sizing-grid">
            <div className="sizing-item action-item">
              <span className="sizing-key">Action</span>
              <span className={`sizing-val action-${raise_sizing.action}`}>
                {raise_sizing.action === "all-in"
                  ? "ALL-IN"
                  : raise_sizing.action.charAt(0).toUpperCase() + raise_sizing.action.slice(1)}
              </span>
            </div>
            {raise_sizing.raise_amount > 0 && (
              <div className="sizing-item">
                <span className="sizing-key">Raise Amount</span>
                <span className="sizing-val">${raise_sizing.raise_amount.toFixed(2)}</span>
              </div>
            )}
            {raise_sizing.raise_pct_pot > 0 && (
              <div className="sizing-item">
                <span className="sizing-key">% of Pot</span>
                <span className="sizing-val">{raise_sizing.raise_pct_pot}%</span>
              </div>
            )}
            <div className="sizing-item">
              <span className="sizing-key">SPR Before</span>
              <span className="sizing-val">{raise_sizing.spr_before}</span>
            </div>
            {raise_sizing.raise_amount > 0 && (
              <>
                <div className="sizing-item">
                  <span className="sizing-key">Pot After Raise</span>
                  <span className="sizing-val">${raise_sizing.pot_after_raise.toFixed(2)}</span>
                </div>
                <div className="sizing-item">
                  <span className="sizing-key">SPR After</span>
                  <span className="sizing-val">{raise_sizing.spr_after}</span>
                </div>
                <div className="sizing-item">
                  <span className="sizing-key">Remaining Stack</span>
                  <span className="sizing-val">${raise_sizing.remaining_stack.toFixed(2)}</span>
                </div>
              </>
            )}
          </div>
          <div className="sizing-reasoning">{raise_sizing.reasoning}</div>
        </div>
      )}

      {strategy && (
        <div className="strategy-section">
          <h3>🧠 Pro Strategy</h3>
          <div className={`strategy-primary action-${strategy.primary_action}`}>
            <span className="strategy-label">{strategy.primary_label}</span>
            <p className="strategy-explanation">{strategy.primary_explanation}</p>
          </div>

          {strategy.advanced_plays && strategy.advanced_plays.length > 0 && (
            <div className="strategy-plays">
              <h4>Advanced Plays</h4>
              {strategy.advanced_plays.map((play, i) => (
                <div className="play-card" key={i}>
                  <div className="play-header">
                    <span className="play-icon">{play.icon}</span>
                    <span className="play-name">{play.name}</span>
                  </div>
                  <p className="play-desc">{play.description}</p>
                  <p className="play-when"><strong>When to use:</strong> {play.when_to_use}</p>
                </div>
              ))}
            </div>
          )}

          {strategy.strategic_tips && strategy.strategic_tips.length > 0 && (
            <div className="strategy-tips">
              <h4>Psychological Edge</h4>
              {strategy.strategic_tips.map((tip, i) => (
                <div className="tip-item" key={i}>{tip}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Results;
