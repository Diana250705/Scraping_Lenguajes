# URL base para la búsqueda de empleo en cada portal
BASE_URLS = {
    "computrabajo": "https://pe.computrabajo.com/trabajo-de",
    "linkedin": "https://www.linkedin.com/jobs/search",
}

# Cabeceras HTTP para evitar bloqueos del servidor
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Tiempos de espera y límites para las peticiones del scraper
REQUEST_TIMEOUT = 10
MAX_PAGES = 3
DELAY_BETWEEN_REQUESTS = 1.5