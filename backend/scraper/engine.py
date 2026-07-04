import concurrent.futures
from backend.scraper.parsers import computrabajo, linkedin

SCRAPERS = {
    "computrabajo": computrabajo.scrape,
    "linkedin": linkedin.scrape,
}


def run_all(query: str, location: str = "Peru", max_pages: int = 2) -> list[dict]:
    all_jobs = []
    seen_ids = set()

    def run_scraper(name: str, fn) -> list[dict]:
        print(f"[Engine] Iniciando {name}...")
        try:
            results = fn(query=query, location=location, max_pages=max_pages)
            print(f"[Engine] {name}: {len(results)} ofertas encontradas")
            return results
        except Exception as e:
            print(f"[Engine] {name} falló: {e}")
            return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_scraper, name, fn): name
            for name, fn in SCRAPERS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            jobs = future.result()
            for job in jobs:
                if job and job.get("id") and job["id"] not in seen_ids:
                    seen_ids.add(job["id"])
                    all_jobs.append(job)

    print(f"[Engine] Total: {len(all_jobs)} ofertas únicas")
    return all_jobs