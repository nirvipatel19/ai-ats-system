"""Shortlisting Agent - Marks candidates as Shortlisted or Rejected based on score."""
import logging
from typing import List

logger = logging.getLogger(__name__)

SHORTLIST_THRESHOLD = 0.6


from agents.skill_agent import normalize_skill

def shortlist_candidates(candidates: List[dict], jd_skills: List[str] = None, threshold: float = SHORTLIST_THRESHOLD) -> List[dict]:
    """
    Mark candidates as 'Shortlisted' if skill match percentage >= threshold.
    Uses normalization to catch 'React' vs 'ReactJS' etc.
    """
    logger.info(f"Running Shortlisting Agent (Criteria: {threshold*100}% tech skill match)...")
    
    if not jd_skills:
        logger.warning("No JD skills extracted. Using AI similarity score as fallback.")
        for c in candidates:
            score = c.get("score", 0)
            c["status"] = "Shortlisted" if score >= threshold else "Rejected"
        return candidates

    # Normalize JD skills for matching
    jd_skills_norm = {normalize_skill(s) for s in jd_skills if normalize_skill(s)}
    total_jd_skills = len(jd_skills_norm)

    for c in candidates:
        cand_skills_norm = {normalize_skill(s) for s in (c.get("skills") or []) if normalize_skill(s)}
        
        # Intersection on normalized skills
        matching_skills = jd_skills_norm.intersection(cand_skills_norm)
        match_count = len(matching_skills)
        
        match_perc = match_count / total_jd_skills if total_jd_skills > 0 else 0
        
        c["skill_match_perc"] = round(match_perc, 4)
        c["status"] = "Shortlisted" if match_perc >= threshold else "Rejected"
        
        logger.info(f"Candidate {c.get('filename')}: Matches {match_count}/{total_jd_skills} skills ({match_perc*100:.1f}%) -> {c['status']}")
    
    return candidates
