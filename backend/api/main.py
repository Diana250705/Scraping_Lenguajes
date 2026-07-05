from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

# Inicialización de la aplicación FastAPI con metadatos del proyecto
app = FastAPI(
    title="JobScraper Perú API",
    description="Scraping de portales laborales peruanos",
    version="1.0.0",
)

# Configuración de CORS para permitir solicitudes desde el frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de las rutas principales (endpoints) de la aplicación
app.include_router(router)


# Ruta básica de salud para verificar que la API está funcionando
@app.get("/health")
def health():
    return {"status": "ok"}