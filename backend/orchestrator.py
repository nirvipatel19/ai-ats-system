"""Agent Orchestrator - Coordinates all agents and combines outputs."""
import logging
from typing import List

from agents.parser_agent import parse_resume
from agents.skill_agent import extract_skills
from agents.matching_agent import compute_similarity
from agents.ranking_agent import rank_candidates
from agents.shortlisting_agent import shortlist_candidates

logger = logging.getLogger(__name__)


def run_pipeline(job_description: str, resume_files: List[tuple[str, bytes]]) -> dict:
    """
    Run the full ATS pipeline for all resumes.
    
    resume_files: List of (filename, pdf_bytes) tuples.
    Returns combined response with ranked candidates and logs.
    """
    logs: List[str] = []
    candidates: List[dict] = []
    
    def log_msg(msg: str):
        logs.append(msg)
        logger.info(msg)
    
    log_msg("=== ATS Pipeline Started ===")
    log_msg(f"Job Description length: {len(job_description)} chars")
    log_msg(f"Resumes to process: {len(resume_files)}")
    
    from concurrent.futures import ThreadPoolExecutor
    
    def process_single_resume(filename, pdf_content):
        log_msg(f"--- Processing: {filename} ---")
        
        # 1. Resume Parser Agent
        parsed = parse_resume(pdf_content, filename)
        if not parsed.get("success"):
            log_msg(f"  Skipping {filename}: Parse failed")
            return {
                "name": filename.replace(".pdf", ""),
                "filename": filename,
                "score": 0.0,
                "status": "Rejected",
                "skills": [],
                "error": parsed.get("error", "Parse failed"),
            }
        
        raw_text = parsed.get("raw_text", "")
        
        # 2. Skill Extraction Agent
        skills = extract_skills(raw_text)
        
        # 3. Matching Agent
        score = compute_similarity(raw_text, job_description)
        
        return {
            "name": parsed.get("name", filename.replace(".pdf", "")),
            "filename": filename,
            "score": score,
            "skills": skills[:10],
        }

    # 0. Extract skills from JD to show what we're looking for
    jd_skills = extract_skills(job_description)
    log_msg(f"Extracted {len(jd_skills)} required skills from JD.")

    # Parallel processing of resumes
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda r: process_single_resume(*r), resume_files))
        candidates.extend(results)
    
    # 4. Ranking Agent
    log_msg("\nRunning Ranking Agent...")
    candidates = rank_candidates(candidates)
    
    # 5. Shortlisting Agent
    log_msg("Running Shortlisting Agent...")
    candidates = shortlist_candidates(candidates, jd_skills=jd_skills)
    
    log_msg("\n=== ATS Pipeline Complete ===")
    
    return {
        "candidates": candidates,
        "logs": logs,
        "jd_skills": jd_skills,
    }
