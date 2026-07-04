def match(job: dict, profile: dict) -> dict:
    breakdown = {
        "title":    score_title(job, profile),
        "salary":   score_salary(job, profile),
        "modality": score_modality(job, profile),
        "location": score_location(job, profile),
        "keywords": score_keywords(job, profile),
    }

    weights = {
        "title":    30,
        "salary":   25,
        "modality": 20,
        "location": 15,
        "keywords": 10,
    }

    total = sum(breakdown[k] * weights[k] for k in breakdown)

    return {
        "breakdown": breakdown,
        "total": round(total),
    }


def score_title(job: dict, profile: dict) -> float:
    if not job.get("title") or not profile.get("title"):
        return 0.5
    job_title = job["title"].lower()
    target = profile["title"].lower()
    if target in job_title or job_title in target:
        return 1.0
    job_words = set(job_title.split())
    target_words = set(target.split())
    overlap = len(job_words & target_words) / max(len(target_words), 1)
    return min(overlap, 1.0)


def score_salary(job: dict, profile: dict) -> float:
    salary = job.get("salary", {})
    s_min = salary.get("min")
    s_max = salary.get("max")
    p_min = profile.get("salary_min") or 0
    p_max = profile.get("salary_max") or float("inf")

    if not s_min and not s_max:
        return 0.5

    mid = s_min if not s_max else (s_min + s_max) / 2

    if p_min <= mid <= p_max:
        return 1.0
    elif mid > p_max:
        return 0.8
    elif mid >= p_min * 0.8:
        return 0.5
    else:
        return 0.1


def score_modality(job: dict, profile: dict) -> float:
    job_mod = (job.get("modality") or "").lower()
    pref_mod = (profile.get("modality") or "").lower()
    if not job_mod or job_mod == "no especificado":
        return 0.5
    if job_mod == pref_mod:
        return 1.0
    if "híbrido" in [job_mod, pref_mod]:
        return 0.7
    return 0.0


def score_location(job: dict, profile: dict) -> float:
    job_loc = (job.get("location") or "").lower()
    pref_loc = (profile.get("location") or "").lower()
    if not job_loc:
        return 0.5
    if pref_loc in job_loc or job_loc in pref_loc:
        return 1.0
    if "lima" in job_loc and "lima" in pref_loc:
        return 1.0
    return 0.3


def score_keywords(job: dict, profile: dict) -> float:
    keywords = [k.lower() for k in profile.get("keywords", [])]
    if not keywords:
        return 0.5
    text = " ".join([
        (job.get("title") or ""),
        (job.get("summary") or ""),
    ]).lower()
    hits = sum(1 for kw in keywords if kw in text)
    return hits / len(keywords)