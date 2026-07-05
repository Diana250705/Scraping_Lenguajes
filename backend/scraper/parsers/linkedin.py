# Realiza web scraping en el portal LinkedIn usando su API de búsqueda pública (guest).

import time
import requests
from bs4 import BeautifulSoup
from backend.config import HEADERS, REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS
from backend.scraper.cleaner import clean_text, normalize_modality

LINKEDIN_SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


# Realiza peticiones paginadas a LinkedIn y devuelve la lista de ofertas
def scrape(query: str, location: str = "Peru", max_pages: int = 2) -> list[dict]:
    jobs = []

    # LinkedIn pagina usando un desplazamiento de 25 en 25
    for start in range(0, max_pages * 25, 25):
        params = {
            "keywords": query,
            "location": location,
            "start": start,
            "f_TPR": "r604800",
        }

        try:
            # Petición HTTP agregando cabecera Referer para evitar bloqueos inmediatos
            response = requests.get(
                LINKEDIN_SEARCH,
                params=params,
                headers={**HEADERS, "Referer": "https://www.linkedin.com/jobs/"},
                timeout=REQUEST_TIMEOUT,
            )
            # Manejo preventivo si se alcanza el límite de solicitudes por IP
            if response.status_code == 429:
                print("[LinkedIn] Rate limit alcanzado. Esperando...")
                time.sleep(10)
                continue
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[LinkedIn] Error: {e}")
            break

        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.find_all("div", class_="base-card")

        if not cards:
            break

        # Procesa cada contenedor de oferta de trabajo
        for card in cards:
            job = parse_card(card)
            if job:
                jobs.append(job)

        time.sleep(DELAY_BETWEEN_REQUESTS * 2)

    return jobs


# Extrae los datos de un contenedor HTML de oferta de LinkedIn
def parse_card(card) -> dict | None:
    try:
        title_el = card.find("h3", class_="base-search-card__title")
        company_el = card.find("h4", class_="base-search-card__subtitle")
        location_el = card.find("span", class_="job-search-card__location")
        metadata_el = card.find("ul", class_="job-search-card__benefits")

        link_el = card.find("a", class_="base-card__full-link")
        job_url = link_el["href"].split("?")[0] if link_el else None
        job_id = job_url.split("-")[-1] if job_url else None

        metadata_text = clean_text(metadata_el.get_text()) if metadata_el else ""

        # Retorna la información formateada. LinkedIn Guest no muestra salarios directamente.
        return {
            "id": f"linkedin_{job_id}",
            "source": "LinkedIn",
            "title": clean_text(title_el.get_text()) if title_el else None,
            "company": clean_text(company_el.get_text()) if company_el else None,
            "location": clean_text(location_el.get_text()) if location_el else None,
            "salary_raw": "",
            "salary": {"min": None, "max": None, "currency": "PEN", "period": None},
            "modality": normalize_modality(metadata_text),
            "summary": None,
            "url": job_url,
            "score": 0,
        }
    except Exception as e:
        print(f"[LinkedIn] Error parseando card: {e}")
        return None