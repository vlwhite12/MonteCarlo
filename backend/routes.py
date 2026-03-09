"""
FastAPI route definitions for the Texas Hold'em equity calculator.
Includes equity calculation, hand analysis, outs, pot odds, and pre-flop chart.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from parallel import run_parallel_simulation
from simulation import card_to_int, RANK_NAMES, SUIT_NAMES, HAND_CATEGORIES
from analysis import (
    get_hand_name, get_sklansky_group, get_preflop_tier,
    classify_hand, calculate_outs, get_preflop_chart, calculate_pot_odds,
    calculate_raise_sizing, get_advanced_strategy,
)

router = APIRouter()


# ── Validators ─────────────────────────────────────────────────────────

def _validate_card(card: str) -> str:
    if len(card) != 2:
        raise ValueError(f"Invalid card format: {card}. Use format like 'As', 'Td'")
    if card[0].upper() not in RANK_NAMES:
        raise ValueError(f"Invalid rank: {card[0]}. Valid: {RANK_NAMES}")
    if card[1].lower() not in SUIT_NAMES:
        raise ValueError(f"Invalid suit: {card[1]}. Valid: {SUIT_NAMES}")
    return card


# ── Request/Response Models ────────────────────────────────────────────

class EquityRequest(BaseModel):
    hole_cards: list[str]
    num_opponents: int = 1
    num_simulations: int = 50000
    community_cards: list[str] = []
    stack_size: float = 0
    pot_size: float = 0

    @field_validator("hole_cards")
    @classmethod
    def validate_hole_cards(cls, v):
        if len(v) != 2:
            raise ValueError("Exactly 2 hole cards required")
        for card in v:
            _validate_card(card)
        if v[0].upper() == v[1].upper():
            raise ValueError("Hole cards must be different")
        return v

    @field_validator("community_cards")
    @classmethod
    def validate_community(cls, v):
        if len(v) not in (0, 3, 4, 5):
            raise ValueError("Community cards must be 0 (pre-flop), 3 (flop), 4 (turn), or 5 (river)")
        seen = set()
        for card in v:
            _validate_card(card)
            key = card[0].upper() + card[1].lower()
            if key in seen:
                raise ValueError(f"Duplicate community card: {card}")
            seen.add(key)
        return v

    @field_validator("num_opponents")
    @classmethod
    def validate_opponents(cls, v):
        if not 1 <= v <= 9:
            raise ValueError("Number of opponents must be between 1 and 9")
        return v

    @field_validator("num_simulations")
    @classmethod
    def validate_simulations(cls, v):
        if not 1000 <= v <= 500000:
            raise ValueError("Number of simulations must be between 1,000 and 500,000")
        return v


class EquityResponse(BaseModel):
    hole_cards: list[str]
    community_cards: list[str]
    num_opponents: int
    win_probability: float
    tie_probability: float
    loss_probability: float
    equity: float
    total_simulations: int
    recommendation: str
    hand_category_breakdown: dict[str, float]
    hand_name: str
    sklansky_group: int
    preflop_tier: str
    street: str
    raise_sizing: dict | None = None
    strategy: dict | None = None


class OutsRequest(BaseModel):
    hole_cards: list[str]
    community_cards: list[str]

    @field_validator("hole_cards")
    @classmethod
    def validate_hole_cards(cls, v):
        if len(v) != 2:
            raise ValueError("Exactly 2 hole cards required")
        for card in v:
            _validate_card(card)
        return v

    @field_validator("community_cards")
    @classmethod
    def validate_community(cls, v):
        if len(v) not in (3, 4):
            raise ValueError("Outs calculation requires 3 (flop) or 4 (turn) community cards")
        for card in v:
            _validate_card(card)
        return v


class PotOddsRequest(BaseModel):
    pot_size: float
    bet_to_call: float
    total_outs: int = 0
    cards_to_come: int = 1

    @field_validator("pot_size")
    @classmethod
    def validate_pot(cls, v):
        if v <= 0:
            raise ValueError("Pot size must be positive")
        return v

    @field_validator("bet_to_call")
    @classmethod
    def validate_bet(cls, v):
        if v <= 0:
            raise ValueError("Bet to call must be positive")
        return v

    @field_validator("cards_to_come")
    @classmethod
    def validate_cards_to_come(cls, v):
        if v not in (1, 2):
            raise ValueError("Cards to come must be 1 or 2")
        return v


# ── Endpoints ──────────────────────────────────────────────────────────

@router.post("/calculate", response_model=EquityResponse)
async def calculate_equity(request: EquityRequest):
    """Calculate Texas Hold'em equity using Monte Carlo simulation.
    Supports pre-flop, flop, turn, and river scenarios."""
    try:
        hole_card_ints = [card_to_int(c) for c in request.hole_cards]
        community_ints = [card_to_int(c) for c in request.community_cards]
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid card: {e}")

    # Check for duplicates between hole and community
    all_cards = hole_card_ints + community_ints
    if len(set(all_cards)) != len(all_cards):
        raise HTTPException(status_code=400, detail="Duplicate cards detected between hole and community cards")

    result = await run_parallel_simulation(
        hole_cards=hole_card_ints,
        num_opponents=request.num_opponents,
        num_simulations=request.num_simulations,
        community_cards=community_ints if community_ints else None,
    )

    # Hand metadata
    hand_name = get_hand_name(hole_card_ints[0], hole_card_ints[1])
    sklansky = get_sklansky_group(hole_card_ints[0], hole_card_ints[1])
    tier = get_preflop_tier(hole_card_ints[0], hole_card_ints[1])

    streets = {0: "Pre-Flop", 3: "Flop", 4: "Turn", 5: "River"}
    street = streets.get(len(community_ints), "Pre-Flop")

    # Raise sizing (only if stack and pot provided)
    raise_sizing = None
    if request.stack_size > 0 and request.pot_size > 0:
        raise_sizing = calculate_raise_sizing(
            equity=result["equity"],
            pot_size=request.pot_size,
            stack_size=request.stack_size,
            num_opponents=request.num_opponents,
            street=street,
        )

    # Advanced strategy recommendations
    strategy = get_advanced_strategy(
        equity=result["equity"],
        street=street,
        num_opponents=request.num_opponents,
        hand_category_breakdown=result["hand_category_breakdown"],
        preflop_tier=tier,
        sklansky_group=sklansky,
        pot_size=request.pot_size,
        stack_size=request.stack_size,
    )

    return EquityResponse(
        hole_cards=[c.upper() for c in request.hole_cards],
        community_cards=[c.upper() for c in request.community_cards],
        num_opponents=request.num_opponents,
        hand_name=hand_name,
        sklansky_group=sklansky,
        preflop_tier=tier,
        street=street,
        raise_sizing=raise_sizing,
        strategy=strategy,
        **result,
    )


@router.post("/outs")
async def calculate_outs_endpoint(request: OutsRequest):
    """Calculate outs and drawing probabilities for flop or turn."""
    try:
        hole_ints = [card_to_int(c) for c in request.hole_cards]
        community_ints = [card_to_int(c) for c in request.community_cards]
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid card: {e}")

    all_cards = hole_ints + community_ints
    if len(set(all_cards)) != len(all_cards):
        raise HTTPException(status_code=400, detail="Duplicate cards detected")

    current = classify_hand(hole_ints + community_ints + [community_ints[0], community_ints[1]])
    outs = calculate_outs(hole_ints, community_ints)

    return {
        "current_hand": current["description"],
        "current_category": current["category"],
        **outs,
    }


@router.post("/pot-odds")
async def pot_odds_endpoint(request: PotOddsRequest):
    """Calculate pot odds and EV analysis."""
    result = calculate_pot_odds(
        pot_size=request.pot_size,
        bet_to_call=request.bet_to_call,
        total_outs=request.total_outs,
        cards_to_come=request.cards_to_come,
    )
    return result


@router.get("/preflop-chart")
async def preflop_chart():
    """Return the 13x13 pre-flop starting hand chart with Sklansky groupings."""
    return get_preflop_chart()


@router.get("/hand-categories")
async def hand_categories():
    """Return the list of hand categories with their indices."""
    return {"categories": [{"index": i, "name": name} for i, name in enumerate(HAND_CATEGORIES)]}


@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}
