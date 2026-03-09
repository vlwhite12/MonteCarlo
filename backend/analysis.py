"""
Hand analysis module — outs calculation, hand strength classification,
drawing probabilities, and pre-flop hand rankings.
"""

from simulation import eval_7, HAND_CATEGORIES, RANK_NAMES, SUIT_NAMES


# ── Pre-flop starting hand strength tiers ─────────────────────────────
# Sklansky-Malmuth groupings (1 = strongest, 8 = weakest, 9 = unranked)
_SKLANSKY = {
    "AA": 1, "KK": 1, "QQ": 1, "JJ": 1, "AKs": 1,
    "TT": 2, "AQs": 2, "AJs": 2, "KQs": 2, "AKo": 2,
    "99": 3, "JTs": 3, "QJs": 3, "KJs": 3, "ATs": 3, "AQo": 3,
    "88": 4, "KTs": 4, "QTs": 4, "J9s": 4, "T9s": 4, "98s": 4,
    "AJo": 4, "KQo": 4,
    "77": 5, "87s": 5, "Q9s": 5, "T8s": 5, "KJo": 5, "QJo": 5,
    "JTo": 5, "76s": 5, "97s": 5, "A9s": 5, "A8s": 5, "A7s": 5,
    "A6s": 5, "A5s": 5, "A4s": 5, "A3s": 5, "A2s": 5,
    "66": 6, "ATo": 6, "55": 6, "86s": 6, "KTo": 6, "QTo": 6,
    "54s": 6, "K9s": 6, "J8s": 6, "75s": 6, "T7s": 6,
    "44": 7, "33": 7, "22": 7, "65s": 7, "J9o": 7, "T9o": 7,
    "98o": 7, "64s": 7, "53s": 7, "85s": 7, "K8s": 7, "K7s": 7,
    "K6s": 7, "K5s": 7, "K4s": 7, "K3s": 7, "K2s": 7,
    "87o": 8, "76o": 8, "Q8s": 8, "J7s": 8, "96s": 8, "43s": 8,
    "T6s": 8, "Q7s": 8, "Q6s": 8, "Q5s": 8, "Q4s": 8, "Q3s": 8,
    "Q2s": 8, "J6s": 8, "J5s": 8, "J4s": 8, "J3s": 8, "J2s": 8,
    "T5s": 8, "T4s": 8, "T3s": 8, "T2s": 8, "95s": 8, "94s": 8,
    "93s": 8, "92s": 8, "84s": 8, "83s": 8, "82s": 8, "74s": 8,
    "73s": 8, "72s": 8, "63s": 8, "62s": 8, "52s": 8, "42s": 8,
    "32s": 8,
}


def get_hand_name(card1_int: int, card2_int: int) -> str:
    """Return the canonical name of a hole card combo, e.g. 'AKs' or 'TTo'."""
    r1, r2 = card1_int >> 2, card2_int >> 2
    s1, s2 = card1_int & 3, card2_int & 3
    high, low = max(r1, r2), min(r1, r2)
    hr = RANK_NAMES[high]
    lr = RANK_NAMES[low]
    if high == low:
        return f"{hr}{lr}"
    suffix = "s" if s1 == s2 else "o"
    return f"{hr}{lr}{suffix}"


def get_sklansky_group(card1_int: int, card2_int: int) -> int:
    """Return the Sklansky-Malmuth group (1-8) or 9 if unranked."""
    name = get_hand_name(card1_int, card2_int)
    return _SKLANSKY.get(name, 9)


def get_preflop_tier(card1_int: int, card2_int: int) -> str:
    """Return a descriptive tier label for a starting hand."""
    group = get_sklansky_group(card1_int, card2_int)
    if group <= 2:
        return "Premium"
    if group <= 4:
        return "Strong"
    if group <= 6:
        return "Playable"
    if group <= 8:
        return "Marginal"
    return "Trash"


def classify_hand(seven_cards: list[int]) -> dict:
    """
    Classify a 7-card hand (2 hole + 5 community).
    Returns the hand category name, score tuple, and description.
    """
    score = eval_7(tuple(seven_cards))
    category = HAND_CATEGORIES[score[0]]

    rank_labels = {i: RANK_NAMES[i] for i in range(13)}
    cat = score[0]

    if cat == 8 and score[1] == 12:
        category = "Royal Flush"
        desc = "Royal Flush"
    elif cat == 8:
        desc = f"Straight Flush, {rank_labels[score[1]]}-high"
    elif cat == 7:
        desc = f"Four of a Kind, {rank_labels[score[1]]}s"
    elif cat == 6:
        desc = f"Full House, {rank_labels[score[1]]}s full of {rank_labels[score[2]]}s"
    elif cat == 5:
        desc = f"Flush, {rank_labels[score[1]]}-high"
    elif cat == 4:
        desc = f"Straight, {rank_labels[score[1]]}-high"
    elif cat == 3:
        desc = f"Three of a Kind, {rank_labels[score[1]]}s"
    elif cat == 2:
        desc = f"Two Pair, {rank_labels[score[1]]}s and {rank_labels[score[2]]}s"
    elif cat == 1:
        desc = f"Pair of {rank_labels[score[1]]}s"
    else:
        desc = f"High Card {rank_labels[score[1]]}"

    return {"category": category, "category_index": cat, "description": desc, "score": score}


def calculate_outs(hole_cards: list[int], community_cards: list[int]) -> dict:
    """
    Calculate outs — cards that improve the hero's hand category on the next street.

    Only meaningful with 3 or 4 community cards (flop or turn).
    Returns a dict of out counts by improvement type and total unique outs.
    """
    if len(community_cards) not in (3, 4):
        return {"total_outs": 0, "improvements": {}, "draw_type": "N/A"}

    dead = set(hole_cards) | set(community_cards)
    remaining = [c for c in range(52) if c not in dead]

    current_seven = hole_cards + community_cards
    # Pad to 7 for flop: we test adding each possible next card
    if len(community_cards) == 3:
        # For flop, test adding 2 more cards — but for outs we check 1-card improvement
        # We'll evaluate with a dummy 7th card for current strength
        # Actually for outs we compare current best 5 from 6 vs best 5 from 7
        current_six = hole_cards + community_cards  # 5 cards, eval best from combos
    current_hand = _best_from_n(current_seven) if len(current_seven) >= 7 else _best_from_n_padded(current_seven)

    current_cat = current_hand[0]
    outs_by_type = {}
    out_cards = []

    for card in remaining:
        test_hand = current_seven + [card]
        if len(test_hand) > 7:
            test_hand = test_hand[:7]
        new_score = _best_from_n(test_hand) if len(test_hand) >= 7 else _best_from_n_padded(test_hand)
        if new_score[0] > current_cat:
            improvement = HAND_CATEGORIES[new_score[0]]
            outs_by_type[improvement] = outs_by_type.get(improvement, 0) + 1
            out_cards.append(card)

    total_outs = len(out_cards)

    # Determine draw type
    draw_type = _classify_draw(total_outs, outs_by_type)

    # Calculate probability of hitting on next card
    cards_remaining = len(remaining)
    probability_next = total_outs / cards_remaining if cards_remaining > 0 else 0

    # If on flop, probability by river (2 cards to come)
    if len(community_cards) == 3:
        miss1 = (cards_remaining - total_outs) / cards_remaining if cards_remaining > 0 else 1
        miss2 = (cards_remaining - 1 - total_outs) / (cards_remaining - 1) if cards_remaining > 1 else 1
        probability_by_river = 1 - (miss1 * miss2)
    else:
        probability_by_river = probability_next

    return {
        "total_outs": total_outs,
        "improvements": outs_by_type,
        "out_cards": [_int_to_str(c) for c in out_cards],
        "draw_type": draw_type,
        "probability_next_card": round(probability_next, 4),
        "probability_by_river": round(probability_by_river, 4),
    }


def _int_to_str(card_int):
    return RANK_NAMES[card_int >> 2] + SUIT_NAMES[card_int & 3]


def _classify_draw(total_outs, outs_by_type):
    if "Flush" in outs_by_type and outs_by_type.get("Flush", 0) >= 8:
        if "Straight" in outs_by_type:
            return "Flush + Straight Draw (Monster)"
        return "Flush Draw"
    if "Straight" in outs_by_type and outs_by_type.get("Straight", 0) >= 6:
        return "Open-Ended Straight Draw"
    if "Straight" in outs_by_type and outs_by_type.get("Straight", 0) >= 3:
        return "Gutshot Straight Draw"
    if total_outs >= 10:
        return "Strong Draw"
    if total_outs >= 4:
        return "Moderate Draw"
    if total_outs > 0:
        return "Weak Draw"
    return "No Draw / Made Hand"


def _best_from_n(cards: list[int]) -> tuple:
    """Best eval_7 from exactly 7 cards."""
    return eval_7(tuple(cards[:7]))


def _best_from_n_padded(cards: list[int]) -> tuple:
    """Evaluate best hand from 5 or 6 cards using combinations to pick 5."""
    from itertools import combinations
    best = (-1,)
    for combo in combinations(cards, min(5, len(cards))):
        # Pad to use eval_7 by duplicating — but actually we need exactly 5
        # Use a simpler eval for <7 cards
        score = _eval_5_or_6(list(combo), cards)
        if score > best:
            best = score
    return best


def _eval_5_or_6(combo, all_cards):
    """Evaluate up to 7 cards by padding if needed."""
    if len(all_cards) >= 7:
        return eval_7(tuple(all_cards[:7]))
    # For 5-6 cards, enumerate all 5-card combos
    from itertools import combinations
    best = (-1,)
    for c5 in combinations(all_cards, 5):
        padded = list(c5) + [c5[0], c5[1]]  # pad to 7 for eval_7
        score = eval_7(tuple(padded))
        if score > best:
            best = score
    return best


def calculate_raise_sizing(
    equity: float,
    pot_size: float,
    stack_size: float,
    num_opponents: int,
    street: str,
) -> dict:
    """
    Calculate recommended raise sizing based on equity, pot, stack, and street.

    Uses a strategy that balances value extraction with pot control:
    - Premium equity (>=65%): Bet large to build the pot / get value
    - Strong equity (55-65%): Standard value bet sizing
    - Moderate equity (45-55%): Smaller bet for pot control
    - Weak equity (<45%): Check or small bluff sizing

    Raise sizes are expressed as fractions of pot and capped by effective stack.
    """
    if pot_size <= 0 or stack_size <= 0:
        return {
            "action": "check",
            "raise_amount": 0,
            "raise_pct_pot": 0,
            "remaining_stack": stack_size,
            "pot_after_raise": pot_size,
            "spr_before": 0,
            "spr_after": 0,
            "reasoning": "Invalid pot or stack size.",
        }

    spr = stack_size / pot_size  # Stack-to-pot ratio

    # Determine base bet sizing as a fraction of pot
    if street == "Pre-Flop":
        # Pre-flop: raise 2.5-4x BB depending on equity and opponents
        # Approximate as pot fraction since we don't track blinds
        if equity >= 0.65:
            bet_frac = 1.0  # pot-sized
        elif equity >= 0.55:
            bet_frac = 0.75
        elif equity >= 0.45:
            bet_frac = 0.5
        else:
            bet_frac = 0.0  # fold / check
    else:
        # Post-flop sizing
        if equity >= 0.75:
            # Very strong: overbet for max value or to deny draws
            bet_frac = 1.25 if spr > 2 else 1.0
        elif equity >= 0.65:
            # Strong: standard large bet
            bet_frac = 0.75
        elif equity >= 0.55:
            # Good: standard bet
            bet_frac = 0.55
        elif equity >= 0.45:
            # Marginal: small bet for pot control / thin value
            bet_frac = 0.33
        else:
            bet_frac = 0.0  # check

    # Adjust for multi-way pots: size up slightly to charge draws
    if num_opponents >= 3 and bet_frac > 0:
        bet_frac = min(bet_frac * 1.2, 1.5)

    # With very low SPR, shove or check
    if spr <= 1.5 and bet_frac > 0 and equity >= 0.45:
        bet_frac = spr  # commit remaining stack
        action = "all-in"
    elif bet_frac <= 0:
        action = "check"
    elif bet_frac >= spr:
        bet_frac = spr
        action = "all-in"
    else:
        action = "raise"

    raise_amount = round(pot_size * bet_frac, 2)
    raise_amount = min(raise_amount, stack_size)  # can't bet more than stack
    remaining = round(stack_size - raise_amount, 2)
    pot_after = round(pot_size + raise_amount, 2)
    spr_after = round(remaining / pot_after, 2) if pot_after > 0 else 0

    # Build reasoning
    eq_pct = round(equity * 100, 1)
    if action == "all-in":
        reasoning = f"With {eq_pct}% equity and an SPR of {spr:.1f}, commit your remaining stack."
    elif action == "check":
        reasoning = f"With {eq_pct}% equity, checking is the safest play to control the pot."
    else:
        frac_label = f"{round(bet_frac * 100)}% pot"
        if equity >= 0.65:
            reasoning = f"Strong {eq_pct}% equity — bet {frac_label} for value."
        elif equity >= 0.55:
            reasoning = f"Solid {eq_pct}% equity — standard {frac_label} bet."
        else:
            reasoning = f"Moderate {eq_pct}% equity — small {frac_label} bet for pot control."

    return {
        "action": action,
        "raise_amount": raise_amount,
        "raise_pct_pot": round(bet_frac * 100, 1),
        "remaining_stack": remaining,
        "pot_after_raise": pot_after,
        "spr_before": round(spr, 2),
        "spr_after": spr_after,
        "reasoning": reasoning,
    }


def get_advanced_strategy(
    equity: float,
    street: str,
    num_opponents: int,
    hand_category_breakdown: dict[str, float],
    preflop_tier: str,
    sklansky_group: int,
    pot_size: float = 0,
    stack_size: float = 0,
) -> dict:
    """
    Generate advanced poker strategy recommendations including deceptive plays.

    Analyzes equity, board texture, position strength, and hand distribution
    to suggest pro-level tactics: check-raising, slow-playing, bluffing,
    semi-bluffing, trapping, floating, and more.
    """
    eq_pct = equity * 100
    spr = stack_size / pot_size if pot_size > 0 and stack_size > 0 else 99
    has_sizing = pot_size > 0 and stack_size > 0

    # Analyze hand distribution for draw potential
    flush_pct = hand_category_breakdown.get("Flush", 0) * 100
    straight_pct = hand_category_breakdown.get("Straight", 0) * 100
    pair_pct = hand_category_breakdown.get("One Pair", 0) * 100
    two_pair_pct = hand_category_breakdown.get("Two Pair", 0) * 100
    trips_pct = hand_category_breakdown.get("Three of a Kind", 0) * 100
    full_house_pct = hand_category_breakdown.get("Full House", 0) * 100
    high_card_pct = hand_category_breakdown.get("High Card", 0) * 100
    made_hand_pct = (two_pair_pct + trips_pct + full_house_pct +
                     hand_category_breakdown.get("Four of a Kind", 0) * 100 +
                     hand_category_breakdown.get("Straight Flush", 0) * 100 +
                     hand_category_breakdown.get("Royal Flush", 0) * 100 +
                     flush_pct + straight_pct)
    draw_heavy = (flush_pct + straight_pct) > 15
    monster = eq_pct >= 75
    strong = 60 <= eq_pct < 75
    decent = 45 <= eq_pct < 60
    weak = 30 <= eq_pct < 45
    air = eq_pct < 30
    heads_up = num_opponents == 1
    multiway = num_opponents >= 3

    primary_action = ""
    primary_label = ""
    primary_explanation = ""
    plays = []  # list of {name, icon, description, when_to_use}

    # ── MONSTER HANDS (75%+) ──────────────────────────────────
    if monster:
        if street == "Pre-Flop":
            primary_action = "slow-play"
            primary_label = "Slow-Play / Trap"
            primary_explanation = (
                f"With {eq_pct:.0f}% equity and a premium hand, consider just calling "
                "instead of 3-betting to disguise your strength. Let aggressive opponents "
                "build the pot for you. If someone raises behind you, spring the trap with a re-raise."
            )
            plays.append({
                "name": "Limp-Reraise",
                "icon": "🪤",
                "description": "Call pre-flop, then re-raise if someone raises behind you. "
                    "This disguises an ultra-strong hand as weakness and baits aggressive players into committing chips.",
                "when_to_use": "Best with AA/KK against aggressive opponents who frequently raise limpers.",
            })
            plays.append({
                "name": "Standard 3-Bet",
                "icon": "💰",
                "description": "The straightforward play — raise to build the pot immediately. "
                    "Less deceptive, but reliable for extracting value from weaker hands that will call.",
                "when_to_use": "Against passive opponents who call too much, or in multiway pots where trapping is risky.",
            })
        else:
            # Post-flop monster
            if heads_up:
                primary_action = "check-raise"
                primary_label = "Check-Raise Trap"
                primary_explanation = (
                    f"With {eq_pct:.0f}% equity, check to your opponent to induce a bet, "
                    "then raise. This extracts maximum value by making them commit chips "
                    "with a weaker hand they wouldn't have called a bet with."
                )
                plays.append({
                    "name": "Check-Raise",
                    "icon": "🎯",
                    "description": "Check, let your opponent bet, then raise big. "
                        "This is the most profitable line with a monster — it builds a bigger pot "
                        "than leading out, and opponents often feel committed after betting.",
                    "when_to_use": "Best heads-up against aggressive bettors. "
                        "They interpret your check as weakness and bet into your trap.",
                })
                plays.append({
                    "name": "Slow-Play (Check-Call)",
                    "icon": "🐌",
                    "description": "Check and just call if they bet. Keep the pot small on this street "
                        "so they stay in, then strike on a later street with a big bet or raise.",
                    "when_to_use": "When the board is dry (few draws) and your opponent might shut down "
                        "if you raise. Gives them a chance to bluff again on the next street.",
                })
            else:
                primary_action = "value-bet"
                primary_label = "Value Bet"
                primary_explanation = (
                    f"With {eq_pct:.0f}% equity in a multiway pot, bet for value. "
                    "Slow-playing is dangerous with multiple opponents — someone likely has "
                    "a draw. Charge them to see the next card."
                )
            plays.append({
                "name": "Overbet for Value",
                "icon": "🔥",
                "description": "Bet more than the pot to maximize value. Opponents with strong-but-second-best "
                    "hands feel pot-committed and call larger bets than they should.",
                "when_to_use": "When you've shown weakness earlier in the hand or when the board "
                    "completes obvious draws — opponents may think you're bluffing.",
            })

    # ── STRONG HANDS (60-75%) ─────────────────────────────────
    elif strong:
        if street == "Pre-Flop":
            primary_action = "raise"
            primary_label = "Value Raise"
            primary_explanation = (
                f"At {eq_pct:.0f}% equity with a strong starting hand, raise for value. "
                "Mix in occasional flat-calls to stay unpredictable."
            )
        elif street in ("Flop", "Turn"):
            primary_action = "bet"
            primary_label = "Value Bet + Blocker"
            primary_explanation = (
                f"With {eq_pct:.0f}% equity, bet to extract value and deny free cards to draws."
            )
            plays.append({
                "name": "Check-Raise (Occasional)",
                "icon": "🎯",
                "description": "Mix in check-raises occasionally to keep opponents guessing. "
                    "If you always bet your strong hands, observant players will exploit your checking range.",
                "when_to_use": "About 20-30% of the time with this hand strength. "
                    "More often against positionally aggressive opponents.",
            })
            plays.append({
                "name": "Block Bet (Small)",
                "icon": "🛡️",
                "description": "Make a small bet (25-33% pot) to \"block\" your opponent from making a larger bet. "
                    "This controls the pot size while still extracting thin value.",
                "when_to_use": "On the turn or river when the board gets scary and you want to "
                    "see a showdown cheaply while still getting paid by weaker hands.",
            })
        else:
            primary_action = "value-bet"
            primary_label = "River Value Bet"
            primary_explanation = (
                f"At {eq_pct:.0f}% equity on the river, bet for value. Size your bet based on "
                "what weaker hands will call."
            )

    # ── DECENT HANDS (45-60%) ─────────────────────────────────
    elif decent:
        if street == "Pre-Flop":
            primary_action = "call"
            primary_label = "Flat Call / Set Mine"
            primary_explanation = (
                f"With {eq_pct:.0f}% equity, calling to see a flop is often better than raising. "
                "If you have a pocket pair, you're set-mining — hoping to hit trips on the flop."
            )
        elif draw_heavy:
            primary_action = "semi-bluff"
            primary_label = "Semi-Bluff"
            primary_explanation = (
                f"At {eq_pct:.0f}% equity with significant draw potential "
                f"(flush: {flush_pct:.0f}%, straight: {straight_pct:.0f}%), "
                "bet aggressively as a semi-bluff. You can win immediately if they fold, "
                "or hit your draw if called."
            )
            plays.append({
                "name": "Semi-Bluff Raise",
                "icon": "💥",
                "description": "Raise or bet with a draw. This is a two-way winning play — "
                    "opponents fold and you win now, or they call and you have strong equity to improve. "
                    "The aggression also sets up bigger pots when you hit.",
                "when_to_use": "With flush draws (9 outs), open-ended straight draws (8 outs), "
                    "or combo draws. Best on the flop with two cards to come.",
            })
            plays.append({
                "name": "Float (Call to Bluff Later)",
                "icon": "🌊",
                "description": "Call a bet on the flop with the intention of bluffing or taking "
                    "the pot on the turn. When your opponent's c-bet folds to aggression on the turn, "
                    "a delayed bet takes down the pot without a made hand.",
                "when_to_use": "Heads-up against a player who c-bets frequently but gives up on the turn. "
                    "Also works when a scare card comes on the turn.",
            })
        else:
            primary_action = "pot-control"
            primary_label = "Pot Control / Check-Call"
            primary_explanation = (
                f"At {eq_pct:.0f}% equity with a marginal made hand, control the pot. "
                "Check-call to keep the pot small and get to showdown cheaply."
            )
            plays.append({
                "name": "Probe Bet",
                "icon": "🔍",
                "description": "Make a small bet (25-33% pot) to probe your opponent's hand strength. "
                    "If they fold, great. If they raise, you can safely fold knowing you're behind.",
                "when_to_use": "When checked to on the flop or turn and you want information "
                    "about your opponent's range without risking much.",
            })

    # ── WEAK HANDS (30-45%) ───────────────────────────────────
    elif weak:
        if draw_heavy and street in ("Flop", "Turn"):
            primary_action = "semi-bluff"
            primary_label = "Semi-Bluff (Drawing)"
            primary_explanation = (
                f"Despite only {eq_pct:.0f}% showdown equity, your draw potential "
                f"(flush: {flush_pct:.0f}%, straight: {straight_pct:.0f}%) makes aggression profitable. "
                "Betting has fold equity plus draw equity — the combination makes this +EV."
            )
            plays.append({
                "name": "Check-Raise Bluff",
                "icon": "🃏",
                "description": "Check, let your opponent bet, then raise as a semi-bluff. "
                    "This represents extreme strength and puts maximum pressure on one-pair hands. "
                    "Even if called, you still have outs to the best hand.",
                "when_to_use": "On draw-heavy boards where you have a flush or straight draw. "
                    "Especially effective when a scare card (ace, flush card) appears.",
            })
        elif street == "River" and heads_up:
            primary_action = "bluff"
            primary_label = "Consider Bluffing"
            primary_explanation = (
                f"At {eq_pct:.0f}% equity on the river, you're unlikely to win at showdown. "
                "A well-timed bluff can steal the pot if the board favors your perceived range."
            )
            plays.append({
                "name": "River Bluff",
                "icon": "🎭",
                "description": "Make a large bet (66-100% pot) on the river representing a strong hand. "
                    "Tell a consistent story — your previous actions should plausibly represent a hand "
                    "that got there on the river. Size matters: bet big enough that calling is painful.",
                "when_to_use": "When a scare card completes a draw on the river, when your opponent "
                    "has shown weakness, or when the board favors your pre-flop range over theirs.",
            })
            plays.append({
                "name": "Thin Value / Block Bet",
                "icon": "🛡️",
                "description": "Make a small bet (25-33% pot) as a blocker. If your opponent was going to "
                    "bluff, they can't. If they have a marginal hand, they might call with worse.",
                "when_to_use": "When you're not sure if you're ahead but want to prevent a bigger bluff.",
            })
        else:
            primary_action = "check-fold"
            primary_label = "Check / Fold"
            primary_explanation = (
                f"With {eq_pct:.0f}% equity against {num_opponents} opponent{'s' if num_opponents > 1 else ''}, "
                "this hand isn't strong enough to continue. Save your chips for a better spot."
            )

    # ── AIR / TRASH (< 30%) ──────────────────────────────────
    else:
        if street == "Pre-Flop":
            primary_action = "fold"
            primary_label = "Fold"
            primary_explanation = (
                f"At {eq_pct:.0f}% equity, this starting hand isn't worth playing. "
                "Discipline is the foundation of winning poker."
            )
        elif heads_up and street in ("Flop", "Turn") and high_card_pct > 40:
            primary_action = "bluff"
            primary_label = "Bluff Opportunity"
            primary_explanation = (
                f"With only {eq_pct:.0f}% equity and mostly high card ({high_card_pct:.0f}%), "
                "your hand has no showdown value. Since you'll lose at showdown anyway, "
                "a well-sized bluff is your only path to profit."
            )
            plays.append({
                "name": "Continuation Bluff",
                "icon": "🎭",
                "description": "Bet as if you have it. On dry boards (no draws), a 50-66% pot bet "
                    "will fold out many missed hands. Your actual cards don't matter — "
                    "you're betting your perceived range, not your hole cards.",
                "when_to_use": "On dry, disconnected boards (e.g. K-7-2 rainbow) where few draws exist "
                    "and the board favors the pre-flop raiser's range.",
            })
            plays.append({
                "name": "Double Barrel",
                "icon": "💣",
                "description": "Bluff the flop AND the turn. Two barrels of aggression tell a convincing story "
                    "of strength. Many opponents give up after calling one street if you fire again.",
                "when_to_use": "When the turn card is a scare card (overcards, flush-completing, "
                    "straight-completing) that your opponent likely fears.",
            })
        else:
            primary_action = "fold"
            primary_label = "Fold / Give Up"
            primary_explanation = (
                f"At {eq_pct:.0f}% equity {'multiway' if multiway else 'heads-up'}, "
                "there's no profitable play. Don't throw good money after bad."
            )

    # ── Universal strategic tips based on position/dynamics ───
    tips = []

    if street != "Pre-Flop" and heads_up:
        tips.append(
            "🧠 Vary your play between value bets, checks, and bluffs with similar hand strengths. "
            "If opponents can predict your action from your bet sizing, they'll exploit you."
        )

    if street in ("Turn", "River") and decent:
        tips.append(
            "📊 Pay attention to opponent bet sizing — a small bet often means they want a cheap showdown "
            "(weak hand), while an overbet usually signals extreme strength or a bluff."
        )

    if monster and street != "Pre-Flop":
        tips.append(
            "⏳ Patience pays. Taking a few extra seconds before check-raising sells the illusion "
            "that you're agonizing over a tough decision. The 'Hollywood' pause makes your trap believable."
        )

    if draw_heavy and street == "Flop":
        tips.append(
            "🔢 With strong draws, consider your opponents' tendencies. Against calling stations, "
            "check and take the free card. Against players who fold to aggression, bet the draw as a bluff."
        )

    if air and heads_up:
        tips.append(
            "🎲 If you're going to bluff, commit to the story. A half-hearted bluff (small bet) "
            "invites calls. Size your bluff as if you have a value hand — typically 66-100% pot."
        )

    if multiway and not monster:
        tips.append(
            "⚠️ Bluffing into multiple opponents is rarely profitable. Each extra player dramatically "
            "reduces fold equity. Save your bluffs for heads-up spots."
        )

    if has_sizing and spr < 3 and street != "Pre-Flop":
        tips.append(
            f"📉 With an SPR of {spr:.1f}, you're in 'commit or fold' territory. "
            "With decent equity, plan to get all-in. With weak equity, don't invest another chip."
        )

    return {
        "primary_action": primary_action,
        "primary_label": primary_label,
        "primary_explanation": primary_explanation,
        "advanced_plays": plays,
        "strategic_tips": tips,
    }


def get_preflop_chart() -> dict:
    """
    Return the full 13x13 pre-flop starting hand chart with Sklansky groups.
    Rows and columns are ranks A-2. Upper triangle = suited, lower = offsuit, diagonal = pairs.
    """
    ranks = list(reversed(RANK_NAMES))  # A, K, Q, ..., 2
    chart = []
    for i, r1 in enumerate(ranks):
        row = []
        for j, r2 in enumerate(ranks):
            if i == j:
                name = f"{r1}{r2}"
            elif i < j:
                name = f"{r1}{r2}s"
            else:
                name = f"{r2}{r1}o"
            group = _SKLANSKY.get(name, 9)
            if group <= 2:
                tier = "premium"
            elif group <= 4:
                tier = "strong"
            elif group <= 6:
                tier = "playable"
            elif group <= 8:
                tier = "marginal"
            else:
                tier = "trash"
            row.append({"name": name, "group": group, "tier": tier})
        chart.append(row)
    return {"ranks": ranks, "chart": chart}


def calculate_pot_odds(pot_size: float, bet_to_call: float, total_outs: int = 0,
                       cards_to_come: int = 1) -> dict:
    """
    Calculate pot odds and compare to drawing odds.

    Args:
        pot_size: current pot size
        bet_to_call: how much hero must call
        total_outs: number of outs
        cards_to_come: 1 (turn or river) or 2 (flop with 2 to come)

    Returns:
        dict with pot odds, implied odds, EV analysis
    """
    if bet_to_call <= 0:
        return {"error": "Bet to call must be positive"}

    pot_odds = bet_to_call / (pot_size + bet_to_call)
    pot_odds_ratio = pot_size / bet_to_call

    # Probability of hitting
    remaining = 52 - 2 - (5 - cards_to_come)  # rough estimate
    if cards_to_come == 1:
        hit_prob = total_outs / remaining if remaining > 0 else 0
    else:
        miss1 = (remaining - total_outs) / remaining if remaining > 0 else 1
        miss2 = (remaining - 1 - total_outs) / (remaining - 1) if remaining > 1 else 1
        hit_prob = 1 - miss1 * miss2

    # Breakeven equity needed
    breakeven = pot_odds

    # Expected value per call
    ev_call = hit_prob * pot_size - (1 - hit_prob) * bet_to_call

    # Required odds to call
    required_ratio = (1 / hit_prob - 1) if hit_prob > 0 else float("inf")

    if hit_prob > pot_odds:
        decision = "Profitable Call (positive EV)"
    else:
        decision = "Unprofitable Call (negative EV)"

    return {
        "pot_odds_pct": round(pot_odds * 100, 1),
        "pot_odds_ratio": f"{pot_odds_ratio:.1f}:1",
        "hand_odds_pct": round(hit_prob * 100, 1),
        "required_pot_ratio": f"{required_ratio:.1f}:1" if required_ratio != float("inf") else "N/A",
        "ev_per_call": round(ev_call, 2),
        "breakeven_equity": round(breakeven * 100, 1),
        "decision": decision,
    }
