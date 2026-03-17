"""In-memory store for resumes, job description, and analysis results."""
from typing import Optional

# filename -> pdf bytes
resumes: dict[str, bytes] = {}

# Current job description
job_description: str = ""

# Last analysis result: {candidates: [...], logs: [...]}
analysis_result: Optional[dict] = None


def clear_all():
    """Reset store (useful for testing)."""
    global resumes, job_description, analysis_result
    resumes = {}
    job_description = ""
    analysis_result = None
