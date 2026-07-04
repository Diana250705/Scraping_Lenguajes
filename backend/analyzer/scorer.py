from backend.analyzer.matcher import match


def score_jobs(jobs: list[dict], profile: dict) -> list[dict]:
    scored = []
    for job in jobs:
        result = match(job, profile)
        job["score"] = result["total"]
        job["score_breakdown"] = result["breakdown"]
        scored.append(job)

    scored.sort(key=lambda j: j["score"], reverse=True)
    return scored