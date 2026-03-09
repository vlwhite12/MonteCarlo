"""
Multiprocessing handler that distributes Monte Carlo simulations across CPU cores.
Uses a persistent ProcessPoolExecutor to avoid pool creation overhead per request.
"""

import asyncio
import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor
from simulation import run_simulation

# Persistent pool — initialized once at import, reused across all requests
_NUM_WORKERS = min(mp.cpu_count(), 8)
_pool: ProcessPoolExecutor | None = None


def _get_pool() -> ProcessPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ProcessPoolExecutor(max_workers=_NUM_WORKERS)
    return _pool


def _worker(args: tuple) -> dict:
    """Worker function for process pool."""
    hole_cards, num_opponents, num_sims, community_cards, seed = args
    return run_simulation(hole_cards, num_opponents, num_sims, community_cards=community_cards, seed=seed)


async def run_parallel_simulation(
    hole_cards: list[int],
    num_opponents: int,
    num_simulations: int = 50000,
    community_cards: list[int] = None,
) -> dict:
    """
    Run Monte Carlo simulations in parallel across multiple CPU cores.
    Non-blocking — awaitable from async FastAPI handlers.

    Args:
        hole_cards: list of 2 ints (0-51) for the player's hole cards
        num_opponents: number of opponents (1-9)
        num_simulations: total simulations to run (split across workers)

    Returns:
        dict with win_probability, tie_probability, loss_probability,
        total_simulations, and recommendation
    """
    pool = _get_pool()
    num_workers = _NUM_WORKERS
    if community_cards is None:
        community_cards = []

    # Split simulations across workers, each with a unique seed
    sims_per_worker = num_simulations // num_workers
    remainder = num_simulations % num_workers

    base_seed = int.from_bytes(os.urandom(4), "big")
    tasks = []
    loop = asyncio.get_event_loop()

    for i in range(num_workers):
        worker_sims = sims_per_worker + (1 if i < remainder else 0)
        seed = base_seed + i
        args = (hole_cards, num_opponents, worker_sims, community_cards, seed)
        tasks.append(loop.run_in_executor(pool, _worker, args))

    results = await asyncio.gather(*tasks)

    # Aggregate results
    total_wins = sum(r["wins"] for r in results)
    total_ties = sum(r["ties"] for r in results)
    total_losses = sum(r["losses"] for r in results)
    total = sum(r["total"] for r in results)

    # Aggregate hand category counts
    hand_categories = [0] * 10
    for r in results:
        for i in range(10):
            hand_categories[i] += r["hand_categories"][i]

    win_prob = total_wins / total
    tie_prob = total_ties / total
    loss_prob = total_losses / total

    # Category percentages
    from simulation import HAND_CATEGORIES
    category_breakdown = {}
    for i, name in enumerate(HAND_CATEGORIES):
        category_breakdown[name] = round(hand_categories[i] / total, 4)

    # Recommendation logic
    equity = win_prob + tie_prob * 0.5
    if equity >= 0.55:
        recommendation = "Raise"
    elif equity >= 0.40:
        recommendation = "Call"
    else:
        recommendation = "Fold"

    return {
        "win_probability": round(win_prob, 4),
        "tie_probability": round(tie_prob, 4),
        "loss_probability": round(loss_prob, 4),
        "equity": round(equity, 4),
        "total_simulations": total,
        "recommendation": recommendation,
        "hand_category_breakdown": category_breakdown,
    }

