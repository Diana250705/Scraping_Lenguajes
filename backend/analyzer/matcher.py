# Evalúa la coincidencia entre una oferta de empleo y el perfil del usuario.


# Calcula el puntaje global ponderado y su desglose para una oferta
def match(job: dict, profile: dict) -> dict:
    # Desglose de puntuaciones individuales
    breakdown = {
        "title":    score_title(job, profile),
        "salary":   score_salary(job, profile),
        "modality": score_modality(job, profile),
        "location": score_location(job, profile),
        "keywords": score_keywords(job, profile),
    }

    # Pesos asignados a cada criterio
    weights = {
        "title":    30,
        "salary":   25,
        "modality": 20,
        "location": 15,
        "keywords": 10,
    }

    # Promedio ponderado final
    total = sum(breakdown[k] * weights[k] for k in breakdown)

    return {
        "breakdown": breakdown,
        "total": round(total),
    }


# Compara las palabras del título del empleo con el título del perfil
def score_title(job: dict, profile: dict) -> float:
    if not job.get("title") or not profile.get("title"):
        return 0.5
    job_title = job["title"].lower()
    target = profile["title"].lower()
    if target in job_title or job_title in target:
        return 1.0
    job_words = set(job_title.split())
    target_words = set(target.split())
    # Proporción de palabras del perfil que están en la oferta
    overlap = len(job_words & target_words) / max(len(target_words), 1)
    return min(overlap, 1.0)


# Salario de la oferta con el rango esperado del perfil
def score_salary(job: dict, profile: dict) -> float:
    salary = job.get("salary", {})
    s_min = salary.get("min")
    s_max = salary.get("max")
    p_min = profile.get("salary_min") or 0
    p_max = profile.get("salary_max") or float("inf")

    if not s_min and not s_max:
        return 0.5 # Puntuación por defecto si no hay información de salario

    mid = s_min if not s_max else (s_min + s_max) / 2

    # Verifica si el salario medio de la oferta cae dentro del rango preferido
    if p_min <= mid <= p_max:
        return 1.0
    elif mid > p_max:
        return 0.8 # El salario es mayor al máximo esperado
    elif mid >= p_min * 0.8:
        return 0.5 # El salario está ligeramente por debajo del mínimo esperado
    else:
        return 0.1 # El salario es muy bajo


# Modalidad de trabajo (remoto, híbrido, presencial)
def score_modality(job: dict, profile: dict) -> float:
    job_mod = (job.get("modality") or "").lower()
    pref_mod = (profile.get("modality") or "").lower()
    if not job_mod or job_mod == "no especificado":
        return 0.5
    if job_mod == pref_mod:
        return 1.0
    if "híbrido" in [job_mod, pref_mod]:
        return 0.7 # Tolerancia parcial si una de las opciones es híbrido
    return 0.0


# Evalúa la coincidencia de ubicación geográfica
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


# Palabras clave (keywords) deseadas están presentes en la oferta
def score_keywords(job: dict, profile: dict) -> float:
    keywords = [k.lower() for k in profile.get("keywords", [])]
    if not keywords:
        return 0.5
    # Busca en el título y descripción/resumen
    text = " ".join([
        (job.get("title") or ""),
        (job.get("summary") or ""),
    ]).lower()
    hits = sum(1 for kw in keywords if kw in text)
    return hits / len(keywords)