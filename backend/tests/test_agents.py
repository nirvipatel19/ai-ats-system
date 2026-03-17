"""Unit tests for ATS agents (skill, ranking, shortlisting - no ML deps)."""
import importlib.util
from pathlib import Path

backend = Path(__file__).parent.parent

def _load(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

skill_mod = _load("skill_agent", backend / "agents" / "skill_agent.py")
ranking_mod = _load("ranking_agent", backend / "agents" / "ranking_agent.py")
shortlist_mod = _load("shortlisting_agent", backend / "agents" / "shortlisting_agent.py")

extract_skills = skill_mod.extract_skills
rank_candidates = ranking_mod.rank_candidates
shortlist_candidates = shortlist_mod.shortlist_candidates


class TestSkillAgent:
    """Tests for extract_skills()."""

    def test_extracts_tech_skills(self):
        text = "I have experience with Python, React, and AWS."
        skills = extract_skills(text)
        assert "python" in skills or "react" in skills or "aws" in skills

    def test_extracts_degrees(self):
        text = "I have a Bachelor of Technology and Master in Computer Science."
        skills = extract_skills(text)
        assert len(skills) > 0

    def test_empty_text_returns_empty_list(self):
        assert extract_skills("") == []
        assert extract_skills("   ") == []

    def test_returns_list_not_set(self):
        skills = extract_skills("Python python")
        assert isinstance(skills, list)
        assert len(skills) <= 30


class TestRankingAgent:
    """Tests for rank_candidates()."""

    def test_sorts_by_score_descending(self):
        candidates = [
            {"filename": "a.pdf", "score": 0.3},
            {"filename": "b.pdf", "score": 0.9},
            {"filename": "c.pdf", "score": 0.6},
        ]
        ranked = rank_candidates(candidates)
        assert ranked[0]["score"] == 0.9
        assert ranked[1]["score"] == 0.6
        assert ranked[2]["score"] == 0.3

    def test_empty_list_returns_empty(self):
        assert rank_candidates([]) == []


class TestShortlistingAgent:
    """Tests for shortlist_candidates()."""

    def test_shortlists_above_threshold(self):
        candidates = [
            {"filename": "a.pdf", "score": 0.8},
            {"filename": "b.pdf", "score": 0.5},
        ]
        result = shortlist_candidates(candidates)
        assert result[0]["status"] == "Shortlisted"
        assert result[1]["status"] == "Rejected"

    def test_threshold_boundary(self):
        candidates = [{"filename": "a.pdf", "score": 0.7}]
        result = shortlist_candidates(candidates)
        assert result[0]["status"] == "Shortlisted"
