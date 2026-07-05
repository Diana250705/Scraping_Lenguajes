import { useState, useCallback } from "react";
import { scrapeJobs, compareJobs } from "../services/api";

// Custom hook para gestionar el estado y la lógica de las ofertas de empleo
export function useJobs() {
    // Estados locales
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selected, setSelected] = useState([]); // IDs de ofertas seleccionadas para comparar
    const [meta, setMeta] = useState({ total: 0, sources: [] });

    // Llama al backend para el scraping y ordenamiento de ofertas
    const search = useCallback(async (searchParams, profile) => {
        setLoading(true);
        setError(null);
        try {
            const result = await scrapeJobs(searchParams, profile);
            setJobs(result.jobs || []);
            setMeta({ total: result.total, sources: result.sources || [] });
        } catch (err) {
            setError(err.response?.data?.detail || "Error al conectar con el servidor");
        } finally {
            setLoading(false);
        }
    }, []);

    // Selecciona/Deselecciona una oferta de trabajo para comparación (límite de 4 ofertas)
    const toggleSelect = useCallback((jobId) => {
        setSelected((prev) =>
            prev.includes(jobId)
                ? prev.filter((id) => id !== jobId)
                : prev.length < 4
                    ? [...prev, jobId]
                    : prev
        );
    }, []);

    // Información detallada de comparación para las ofertas seleccionadas
    const getComparison = useCallback(async () => {
        if (selected.length < 2) return null;
        const result = await compareJobs(selected);
        return result.jobs;
    }, [selected]);

    // Aplica filtros locales sobre la lista de ofertas obtenidas
    const filterJobs = useCallback(
        (filterParams) => {
            const { minScore, modality, source, minSalary } = filterParams || {};
            return jobs.filter((j) => {
                // Filtro por puntaje mínimo
                if (minScore !== undefined && minScore !== null && minScore > 0 && j.score < minScore) return false;
                // Filtro por modalidad de trabajo
                if (modality && j.modality !== modality) return false;
                // Filtro por portal de origen
                if (source && j.source !== source) return false;
                // Filtro por salario mínimo
                if (minSalary && j.salary?.min && j.salary.min < minSalary) return false;
                return true;
            });
        },
        [jobs]
    );

    return {
        jobs,
        loading,
        error,
        meta,
        selected,
        search,
        toggleSelect,
        getComparison,
        filterJobs,
    };
}