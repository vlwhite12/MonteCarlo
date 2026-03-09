"""
FastAPI route definitions for the Texas Hold'em equity calculator.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from parallel import run_parallel_simulation
from simulation import card_to_int, RANK_NAMES, SUIT_NAMES

router = APIRouter()


class EquityRequest(BaseModel):
    hole_cards: list[str]
    num_opponents: int = 1
    num_simulations: int = 50000

    @field_validator("hole_cards")
    @classmethod
    def validate_hole_cards(cls, v):
        if len(v) != 2:
            raise ValueError("Exactly 2 hole cards required")
        for card in v:
            if len(card) != 2:
                raise ValueError(f"Invalid card format: {card}. Use format like 'As', 'Td'")
            if card[0].upper() not in RANK_NAMES:
                raise ValueError(f"Invalid rank: {card[0]}. Valid: {RANK_NAMES}")
            if card[1].lower() not in SUIT_NAMES:
                raise ValueError(f"Invalid suit: {card[1]}. Valid: {SUIT_NAMES}")
        if v[0].upper() == v[1].upper():
            raise ValueError("Hole cards must be different")
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
    num_opponents: int
    win_probability: float
    tie_probability: float
    loss_probability: float
    equity: float
    total_simulations: int
    recommendation: str


@router.post("/calculate", response_model=EquityResponse)
async def calculate_equity(request: EquityRequest):
    """Calculate Texas Hold'em equity using Monte Carlo simulation."""
    try:
        hole_card_ints = [card_to_int(c) for c in request.hole_cards]
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid card: {e}")

    result = await run_parallel_simulation(
        hole_cards=hole_card_ints,
        num_opponents=request.num_opponents,
        num_simulations=request.num_simulations,
    )

    return EquityResponse(
        hole_cards=[c.upper() for c in request.hole_cards],
        num_opponents=request.num_opponents,
        **result,
    )


@router.get("/health")
async def health_check():
    return {"status": "ok"}
