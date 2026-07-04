import axios from "axios";

const BASE_URL = "http://localhost:8000/api";

export const api = axios.create({
    baseURL: BASE_URL,
    timeout: 60000,
});

export async function scrapeJobs(searchParams, profile) {
    const { data } = await api.post("/scrape", {
        search: searchParams,
        profile,
    });
    return data;
}

export async function compareJobs(jobIds) {
    const { data } = await api.post("/compare", jobIds);
    return data;
}

export async function clearCache() {
    const { data } = await api.delete("/cache");
    return data;
}