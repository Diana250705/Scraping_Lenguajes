from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.scraper.engine import run_all
from backend.analyzer.scorer import score_jobs
from backend.database.models import create_table, save_jobs, get_all_jobs

router = APIRouter(prefix="/api")

_cache: dict = {}

class SearchRequest(BaseModel):
    query: str
    location: str = "Lima"
    max_pages: int = 2


class UserProfile(BaseModel):
    title: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    modality: Optional[str] = None
    location: Optional[str] = "Lima"
    experience: Optional[int] = 0
    keywords: list[str] = []


class ScrapeRequest(BaseModel):
    search: SearchRequest
    profile: UserProfile


@router.post("/scrape")
async def scrape_jobs(req: ScrapeRequest):
    cache_key = f"{req.search.query}_{req.search.location}_{req.search.max_pages}"

    if cache_key in _cache:
        jobs = _cache[cache_key]
    else:
        jobs = run_all(
            query=req.search.query,
            location=req.search.location,
            max_pages=req.search.max_pages,
        )
        _cache[cache_key] = jobs

    if not jobs:
        return {"jobs": [], "total": 0, "message": "Sin resultados"}

    ranked = score_jobs(jobs, req.profile.model_dump())

    return {
        "jobs": ranked,
        "total": len(ranked),
        "sources": list({j["source"] for j in ranked}),
    }


@router.get("/jobs")
async def get_cached_jobs():
    all_jobs = []
    for jobs in _cache.values():
        all_jobs.extend(jobs)
    return {"jobs": all_jobs, "total": len(all_jobs)}


@router.get("/jobs/saved")
async def get_saved_jobs():
    """Retorna todas las ofertas guardadas."""
    jobs = get_all_jobs()
    return {"jobs": jobs, "total": len(jobs)}


@router.post("/compare")
async def compare_jobs(job_ids: list[str]):
    all_jobs = []
    for jobs in _cache.values():
        all_jobs.extend(jobs)
    selected = [j for j in all_jobs if j["id"] in job_ids]
    if not selected:
        raise HTTPException(404, "No se encontraron las ofertas indicadas")
    return {"jobs": selected}

@router.post("/export")
async def export_jobs(req: ScrapeRequest):
    """Crea la tabla si no existe y guarda los jobs del cache."""
    cache_key = f"{req.search.query}_{req.search.location}_{req.search.max_pages}"

    # Buscar en todas las keys del cache que contengan el query
    jobs = _cache.get(cache_key)
    if not jobs:
        for key, cached_jobs in _cache.items():
            if req.search.query.lower() in key.lower():
                jobs = cached_jobs
                break

    if not jobs:
        raise HTTPException(404, "No hay resultados para exportar. Haz una búsqueda primero.")

    ranked = score_jobs(jobs, req.profile.model_dump())
    create_table()
    save_jobs(ranked, req.search.query)

    return {"message": f"{len(ranked)} ofertas exportadas"}
@router.delete("/cache")
async def clear_cache():
    _cache.clear()
    return {"message": "Cache eliminado"}