import axios from "axios";

const BASE_URL = "http://localhost:8000/api";

// Cliente Axios con URL base del backend
export const api = axios.create({
    baseURL: BASE_URL,
    timeout: 60000,
});

// Petición POST al endpoint de scraping enviando criterios y perfil
export async function scrapeJobs(searchParams, profile) {
    const { data } = await api.post("/scrape", {
        search: searchParams,
        profile,
    });
    return data;
}

// Lista de IDs al endpoint de comparación para obtener sus detalles resumidos
export async function compareJobs(jobIds) {
    const { data } = await api.post("/compare", jobIds);
    return data;
}

// Limpiar resultados almacenados temporalmente
export async function clearCache() {
    const { data } = await api.delete("/cache");
    return data;
}