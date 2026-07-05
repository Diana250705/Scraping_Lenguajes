# Coordina y ejecuta en paralelo los scrapers de las distintas plataformas.

import concurrent.futures
from backend.scraper.parsers import computrabajo, linkedin

# Diccionario de funciones de scraping
SCRAPERS = {
    "computrabajo": computrabajo.scrape,
    "linkedin": linkedin.scrape,
}

# Ejecuta todos los scrapers en paralelo y consolida los resultados eliminando duplicados
def run_all(query: str, location: str = "Peru", max_pages: int = 2) -> list[dict]:
    all_jobs = []
    seen_ids = set()

    # Función interna para ejecutar un scraper de forma segura capturando errores
    def run_scraper(name: str, fn) -> list[dict]:
        print(f"[Engine] Iniciando {name}...")
        try:
            results = fn(query=query, location=location, max_pages=max_pages)
            print(f"[Engine] {name}: {len(results)} ofertas encontradas")
            return results
        except Exception as e:
            print(f"[Engine] {name} falló: {e}")
            return []

    # Ejecución paralela utilizando un pool de hilos
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_scraper, name, fn): name
            for name, fn in SCRAPERS.items()
        }
        # Recopila los resultados a medida que cada scraper finaliza
        for future in concurrent.futures.as_completed(futures):
            jobs = future.result()
            for job in jobs:
                # Evita ofertas repetidas mediante su ID único
                if job and job.get("id") and job["id"] not in seen_ids:
                    seen_ids.add(job["id"])
                    all_jobs.append(job)

    print(f"[Engine] Total: {len(all_jobs)} ofertas únicas")
    return all_jobs