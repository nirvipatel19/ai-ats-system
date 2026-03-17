"""Shortlisting Agent - Marks candidates as Shortlisted or Rejected based on score."""
import logging
from typing import List

logger = logging.getLogger(__name__)

SHORTLIST_THRESHOLD = 0.6


def shortlist_candidates(candidates: List[dict], jd_skills: List[str] = None, threshold: float = SHORTLIST_THRESHOLD) -> List[dict]:
    """
    Mark candidates as 'Shortlisted' if skill match percentage >= threshold.
    """
    logger.info(f"Running Shortlisting Agent (Criteria: {threshold*100}% tech skill match)...")
    
    # If no skills were extracted from JD, fallback to similarity score
    if not jd_skills:
        logger.warning("No JD skills extracted. Using AI similarity score as fallback.")
        for c in candidates:
            score = c.get("score", 0)
            c["status"] = "Shortlisted" if score >= threshold else "Rejected"
        return candidates

    jd_skills_set = {s.lower() for s in jd_skills}
    total_jd_skills = len(jd_skills_set)

    for c in candidates:
        cand_skills_set = {s.lower() for s in (c.get("skills") or [])}
        
        # Intersection: find skills present in both
        matching_skills = jd_skills_set.intersection(cand_skills_set)
        match_count = len(matching_skills)
        
        match_perc = match_count / total_jd_skills
        
        # Store the specific match for transparency
        c["skill_match_perc"] = round(match_perc, 4)
        c["status"] = "Shortlisted" if match_perc >= threshold else "Rejected"
        
        logger.info(f"Candidate {c.get('filename')}: Matches {match_count}/{total_jd_skills} skills ({match_perc*100:.1f}%) -> {c['status']}")
    
    return candidates
