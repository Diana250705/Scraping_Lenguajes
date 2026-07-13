from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.scraper.engine import run_all
from backend.analyzer.scorer import score_jobs
from backend.database.models import create_table, save_jobs, get_all_jobs

# Definición del enrutador de FastAPI para el prefijo /api
router = APIRouter(prefix="/api")

# Caché en memoria para guardar las búsquedas temporalmente
_cache: dict = {}

# Modelo para los parámetros de búsqueda de empleo
class SearchRequest(BaseModel):
    query: str
    location: str = "Lima"
    max_pages: int = 2

# Modelo para el perfil profesional del usuario (usado en el scoring)
class UserProfile(BaseModel):
    title: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    modality: Optional[str] = None
    location: Optional[str] = "Lima"
    experience: Optional[int] = 0
    keywords: list[str] = []


# Modelo que agrupa la búsqueda y el perfil del usuario
class ScrapeRequest(BaseModel):
    search: SearchRequest
    profile: UserProfile


# Endpoint para buscar y clasificar ofertas de empleo
@router.post("/scrape")
async def scrape_jobs(req: ScrapeRequest):
    cache_key = f"{req.search.query}_{req.search.location}_{req.search.max_pages}"

    # Recupera del caché o ejecuta los scrapers correspondientes
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

    # Evalúa y ordena los empleos según el perfil del usuario
    ranked = score_jobs(jobs, req.profile.model_dump())

    return {
        "jobs": ranked,
        "total": len(ranked),
        "sources": list({j["source"] for j in ranked}),
    }


# Endpoint para obtener todos los empleos en el caché actual
@router.get("/jobs")
async def get_cached_jobs():
    all_jobs = []
    for jobs in _cache.values():
        all_jobs.extend(jobs)
    return {"jobs": all_jobs, "total": len(all_jobs)}


# Endpoint para obtener todas las ofertas guardadas en la base de datos
@router.get("/jobs/saved")
async def get_saved_jobs():
    """Retorna todas las ofertas guardadas."""
    jobs = get_all_jobs()
    return {"jobs": jobs, "total": len(jobs)}


# Endpoint para comparar ofertas específicas por sus IDs
@router.post("/compare")
async def compare_jobs(job_ids: list[str]):
    all_jobs = []
    for jobs in _cache.values():
        all_jobs.extend(jobs)
    selected = [j for j in all_jobs if j["id"] in job_ids]
    if not selected:
        raise HTTPException(404, "No se encontraron las ofertas indicadas")
    return {"jobs": selected}


# Modelo que agrupa la búsqueda, el perfil y los IDs opcionales para exportar
class ExportRequest(BaseModel):
    search: SearchRequest
    profile: UserProfile
    job_ids: Optional[list[str]] = None


# Endpoint para guardar los resultados del caché en la base de datos
@router.post("/export")
async def export_jobs(req: ExportRequest):
    """Crea la tabla si no existe y guarda los jobs del cache (filtrando por job_ids si se proveen)."""
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
    
    # Si se especificaron IDs, se filtra para exportar y reportar solo esos
    if req.job_ids is not None:
        ranked = [j for j in ranked if j["id"] in req.job_ids]

    create_table()
    save_jobs(ranked, req.search.query)

    return {"message": f"{len(ranked)} ofertas exportadas"}



# Endpoint para limpiar la memoria caché
@router.delete("/cache")
async def clear_cache():
    _cache.clear()
    return {"message": "Cache eliminado"}