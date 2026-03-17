"""Ranking Agent - Sorts candidates by similarity score."""
import logging
from typing import List

logger = logging.getLogger(__name__)


def rank_candidates(candidates: List[dict]) -> List[dict]:
    """Sort candidates by score descending (highest first)."""
    logger.info("Running Ranking Agent...")
    
    if not candidates:
        logger.info("Ranking Agent complete. No candidates to rank.")
        return []
    
    sorted_list = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
    logger.info(f"Ranking Agent complete. Ranked {len(sorted_list)} candidates.")
    return sorted_list
