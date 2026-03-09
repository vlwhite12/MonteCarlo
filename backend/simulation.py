"""
Core Monte Carlo simulation engine for Texas Hold'em equity calculation.
Uses NumPy for bulk random dealing and pure-Python for fast hand evaluation.
Supports pre-flop, flop, turn, and river scenarios with community cards.
"""

import numpy as np
from itertools import combinations

# Card encoding: 0-51
# rank = card >> 2  (0=2, 1=3, ..., 8=T, 9=J, 10=Q, 11=K, 12=A)
# suit = card & 3   (0=clubs, 1=diamonds, 2=hearts, 3=spades)

RANK_NAMES = "23456789TJQKA"
SUIT_NAMES = "cdhs"

HAND_CATEGORIES = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind",
    "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush",
    "Royal Flush"
]


def card_to_int(card_str: str) -> int:
    """Convert a card string like 'As' or 'Td' to an integer 0-51."""
    rank = RANK_NAMES.index(card_str[0].upper())
    suit = SUIT_NAMES.index(card_str[1].lower())
    return rank * 4 + suit


def int_to_card(card_int: int) -> str:
    """Convert an integer 0-51 back to a card string."""
    return RANK_NAMES[card_int // 4] + SUIT_NAMES[card_int % 4]


def cards_to_ints(card_strs: list[str]) -> list[int]:
    """Convert a list of card strings to integers."""
    return [card_to_int(c) for c in card_strs]


def _find_straight_rc(rc):
    """Find highest straight from rank counts array. Returns high rank or -1."""
    for high in range(12, 3, -1):
        if rc[high] and rc[high - 1] and rc[high - 2] and rc[high - 3] and rc[high - 4]:
            return high
    # Wheel: A-2-3-4-5
    if rc[12] and rc[0] and rc[1] and rc[2] and rc[3]:
        return 3
    return -1


def _find_straight_in(sorted_ranks):
    """Find highest straight from a sorted-descending list of unique ranks."""
    seen = set(sorted_ranks)
    for high in range(12, 3, -1):
        if high in seen and (high-1) in seen and (high-2) in seen and (high-3) in seen and (high-4) in seen:
            return high
    if 12 in seen and 0 in seen and 1 in seen and 2 in seen and 3 in seen:
        return 3
    return -1


def eval_7(cards):
    """
    Evaluate best 5-card hand from 7 cards directly. Pure Python for speed.
    Returns a tuple that can be compared with < > == for hand ranking.

    Hand category values:
    8: Straight Flush
    7: Four of a Kind
    6: Full House
    5: Flush
    4: Straight
    3: Three of a Kind
    2: Two Pair
    1: One Pair
    0: High Card
    """
    # Pre-compute ranks and suits using bit operations
    r0 = cards[0] >> 2; s0 = cards[0] & 3
    r1 = cards[1] >> 2; s1 = cards[1] & 3
    r2 = cards[2] >> 2; s2 = cards[2] & 3
    r3 = cards[3] >> 2; s3 = cards[3] & 3
    r4 = cards[4] >> 2; s4 = cards[4] & 3
    r5 = cards[5] >> 2; s5 = cards[5] & 3
    r6 = cards[6] >> 2; s6 = cards[6] & 3

    ranks = (r0, r1, r2, r3, r4, r5, r6)
    suits = (s0, s1, s2, s3, s4, s5, s6)

    # Rank counts
    rc = [0] * 13
    rc[r0] += 1; rc[r1] += 1; rc[r2] += 1; rc[r3] += 1
    rc[r4] += 1; rc[r5] += 1; rc[r6] += 1

    # Suit counts
    sc = [0] * 4
    sc[s0] += 1; sc[s1] += 1; sc[s2] += 1; sc[s3] += 1
    sc[s4] += 1; sc[s5] += 1; sc[s6] += 1

    # Check for flush
    flush_suit = -1
    if sc[0] >= 5: flush_suit = 0
    elif sc[1] >= 5: flush_suit = 1
    elif sc[2] >= 5: flush_suit = 2
    elif sc[3] >= 5: flush_suit = 3

    if flush_suit >= 0:
        flush_ranks = sorted(
            [ranks[i] for i in range(7) if suits[i] == flush_suit],
            reverse=True
        )
        sf = _find_straight_in(flush_ranks)
        if sf >= 0:
            return (8, sf)
        return (5, flush_ranks[0], flush_ranks[1], flush_ranks[2], flush_ranks[3], flush_ranks[4])

    # Categorize ranks by count (descending rank order)
    fours = []
    threes = []
    pairs = []
    singles = []
    for r in range(12, -1, -1):
        c = rc[r]
        if c == 4: fours.append(r)
        elif c == 3: threes.append(r)
        elif c == 2: pairs.append(r)
        elif c == 1: singles.append(r)

    # Four of a kind
    if fours:
        # Best kicker from remaining cards
        kicker = threes[0] if threes else (pairs[0] if pairs else singles[0])
        return (7, fours[0], kicker)

    # Full house
    if len(threes) >= 2:
        return (6, threes[0], threes[1])
    if threes and pairs:
        return (6, threes[0], pairs[0])

    # Straight
    st = _find_straight_rc(rc)
    if st >= 0:
        return (4, st)

    # Three of a kind
    if threes:
        # Top 2 kickers
        kickers = (pairs + singles)[:2]
        return (3, threes[0], kickers[0], kickers[1])

    # Two pair
    if len(pairs) >= 2:
        remaining = []
        if len(pairs) > 2:
            remaining.append(pairs[2])
        remaining.extend(singles)
        return (2, pairs[0], pairs[1], remaining[0] if remaining else 0)

    # One pair
    if pairs:
        kickers = singles[:3]
        return (1, pairs[0], kickers[0], kickers[1], kickers[2] if len(kickers) > 2 else 0)

    # High card
    return (0, singles[0], singles[1], singles[2], singles[3], singles[4])


def run_simulation(hole_cards: list[int], num_opponents: int, num_simulations: int,
                    community_cards: list[int] = None, seed: int = None) -> dict:
    """
    Run Monte Carlo simulations for Texas Hold'em equity.

    Supports any board state: pre-flop (0 community), flop (3), turn (4), river (5).

    Args:
        hole_cards: list of 2 ints (0-51) representing the player's hole cards
        num_opponents: number of opponents (1-9)
        num_simulations: how many hands to simulate
        community_cards: optional list of 0, 3, 4, or 5 known community cards
        seed: optional RNG seed for reproducibility

    Returns:
        dict with wins/ties/losses/total counts and hand_categories breakdown
    """
    if community_cards is None:
        community_cards = []

    rng = np.random.default_rng(seed)
    dead_cards = set(hole_cards) | set(community_cards)
    deck = np.array([c for c in range(52) if c not in dead_cards], dtype=np.int32)
    deck_size = len(deck)

    wins = 0
    ties = 0
    losses = 0

    # Track what hand category the hero makes
    hand_categories = [0] * 10  # indexed by category 0-9 (9 = Royal Flush)

    community_needed = 5 - len(community_cards)
    cards_needed = community_needed + num_opponents * 2
    h0, h1 = hole_cards[0], hole_cards[1]
    fixed_community = tuple(community_cards)
    num_fixed = len(fixed_community)

    # Pre-generate all random indices in bulk for speed
    all_deals = np.empty((num_simulations, cards_needed), dtype=np.int32)
    for i in range(num_simulations):
        all_deals[i] = rng.choice(deck_size, size=cards_needed, replace=False)

    deck_list = deck.tolist()

    for i in range(num_simulations):
        deal_idx = all_deals[i]
        dealt = [deck_list[j] for j in deal_idx]

        # Build full 5-card community
        if num_fixed == 0:
            c0, c1, c2, c3, c4 = dealt[0], dealt[1], dealt[2], dealt[3], dealt[4]
        elif num_fixed == 3:
            c0, c1, c2 = fixed_community[0], fixed_community[1], fixed_community[2]
            c3, c4 = dealt[0], dealt[1]
        elif num_fixed == 4:
            c0, c1, c2, c3 = fixed_community[0], fixed_community[1], fixed_community[2], fixed_community[3]
            c4 = dealt[0]
        else:  # 5
            c0, c1, c2, c3, c4 = fixed_community

        # Evaluate hero
        hero_score = eval_7((h0, h1, c0, c1, c2, c3, c4))
        cat_idx = hero_score[0]
        # Royal flush = straight flush (8) with ace-high (12)
        if cat_idx == 8 and hero_score[1] == 12:
            hand_categories[9] += 1
        else:
            hand_categories[cat_idx] += 1

        # Evaluate opponents
        best_villain = (-1,)
        opp_base = community_needed
        for opp in range(num_opponents):
            base = opp_base + opp * 2
            opp_score = eval_7((dealt[base], dealt[base + 1], c0, c1, c2, c3, c4))
            if opp_score > best_villain:
                best_villain = opp_score

        if hero_score > best_villain:
            wins += 1
        elif hero_score == best_villain:
            ties += 1
        else:
            losses += 1

    return {
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "total": num_simulations,
        "hand_categories": hand_categories,
    }
