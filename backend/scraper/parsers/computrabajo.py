# Realiza web scraping en el portal Computrabajo Perú

import time
import requests
from bs4 import BeautifulSoup
from backend.config import BASE_URLS, HEADERS, REQUEST_TIMEOUT, DELAY_BETWEEN_REQUESTS
from backend.scraper.cleaner import clean_text, normalize_salary, normalize_modality, normalize_experience


# Realiza peticiones paginadas y devuelve la lista de ofertas obtenidas
def scrape(query: str, location: str = "", max_pages: int = 3) -> list[dict]:
    jobs = []
    query_slug = query.replace(" ", "-").lower()

    for page in range(1, max_pages + 1):
        url = f"{BASE_URLS['computrabajo']}-{query_slug}"
        params = {"p": page}
        
        try:
            # Obtiene el HTML de la página de resultados
            response = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[Computrabajo] Error página {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.find_all("article", class_="box_offer")

        if not cards:
            break

        # Procesa cada contenedor (card) de oferta de trabajo
        for card in cards:
            job = parse_card(card)
            if job:
                jobs.append(job)

        # Espera un breve tiempo para no sobrecargar el servidor
        if page < max_pages:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    return jobs


# Extrae los datos detallados de un contenedor de oferta de Computrabajo
def parse_card(card) -> dict | None:
    try:
        title_el = card.find("h2")
        company_el = card.find("p", class_="dFlex")
        location_el = card.find("p", class_="fs16 fc_base mt5")
        detail_el = card.find("p", class_="fs13 fc_aux mt15")

        link_el = card.find("a")
        job_id = card.get("data-id")
        if not job_id and link_el:
            clean_href = link_el["href"].split("#")[0].split("?")[0]
            job_id = clean_href.split("/")[-1]

        job_url = None
        if link_el:
            clean_href = link_el["href"].split("#")[0].split("?")[0]
            job_url = f"https://pe.computrabajo.com{clean_href}"

        raw_detail = clean_text(detail_el.get_text()) if detail_el else ""

        # Extrae información del salario y la modalidad de los elementos span
        raw_salary = ""
        raw_modality = ""
        for span in card.find_all("span", class_="dIB"):
            span_text = clean_text(span.get_text())
            if span.find(class_="i_salary") or "s/." in span_text.lower():
                raw_salary = span_text
            elif span.find(class_="i_home_office") or any(kw in span_text.lower() for kw in ["remoto", "presencial", "híbrido", "hibrido", "mixto", "casa", "oficina", "teletrabajo"]):
                raw_modality = span_text

        title_text = ""
        if title_el:
            title_link = title_el.find("a")
            title_text = title_link.get_text() if title_link else title_el.get_text()
            # Limpia palabras residuales del título ("postulado", "vista")
            import re
            for badge in ["postulado", "vista"]:
                title_text = re.sub(rf"\b{badge}\b", "", title_text, flags=re.IGNORECASE).strip()
            # Remueve espacios
            title_text = re.sub(r"\s+", " ", title_text).strip()

        # Retorna el diccionario con la información formateada y normalizada
        return {
            "id": f"computrabajo_{job_id}" if job_id else None,
            "source": "Computrabajo",
            "title": clean_text(title_text) if title_text else None,
            "company": clean_text(company_el.get_text()) if company_el else None,
            "location": clean_text(location_el.get_text()) if location_el else None,
            "salary_raw": raw_salary,
            "salary": normalize_salary(raw_salary),
            "modality": normalize_modality(raw_modality),
            "experience_years": normalize_experience(raw_detail),
            "summary": raw_detail,
            "url": job_url,
            "score": 0,
        }
    except Exception as e:
        print(f"[Computrabajo] Error parseando card: {e}")
        return None