import json
import os
from typing import List, Dict, Any

def _load_jobs_db() -> List[Dict[str, Any]]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jobs_path = os.path.join(base_dir, "jobs_db", "sample_job.json")

    if not os.path.exists(jobs_path):
        raise FileNotFoundError(f"Jobs DB not found at {jobs_path}")

    with open(jobs_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _score_job(skills: List[str], job: Dict[str, Any]) -> int:
    job_skills = {s.strip().lower() for s in job.get("skills", [])}
    user_skills = {s.strip().lower() for s in skills}
    return len(job_skills.intersection(user_skills))

def recommend_jobs(skills: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
    jobs = _load_jobs_db()
    scored = []

    for job in jobs:
        score = _score_job(skills, job)
        if score > 0:
            scored.append({**job, "match_score": score})

    if not scored:
        return [{
            "id": "generic-it",
            "title": "General IT / Software Role",
            "skills": [],
            "location": "Remote / Flexible",
            "match_score": 0,
            "description": "Generic software/IT role – your skills may be applicable across multiple positions."
        }]

    scored.sort(key=lambda j: j["match_score"], reverse=True)
    return scored[:top_k]