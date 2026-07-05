# analyzer/scorer.py
# Califica y ordena un listado de ofertas de trabajo según la afinidad con el perfil del usuario.

from backend.analyzer.matcher import match


# Recibe una lista de empleos, calcula su puntaje y los devuelve ordenados de mayor a menor afinidad
def score_jobs(jobs: list[dict], profile: dict) -> list[dict]:
    scored = []
    for job in jobs:
        # Calcula la coincidencia usando el motor matcher
        result = match(job, profile)
        job["score"] = result["total"]
        job["score_breakdown"] = result["breakdown"]
        scored.append(job)

    # Ordena la lista resultante descendentemente por su puntaje
    scored.sort(key=lambda j: j["score"], reverse=True)
    return scored