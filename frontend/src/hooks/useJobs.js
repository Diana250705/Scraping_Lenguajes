import { useState, useCallback } from "react";
import { scrapeJobs, compareJobs } from "../services/api";

export function useJobs() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selected, setSelected] = useState([]);
    const [meta, setMeta] = useState({ total: 0, sources: [] });

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

    const toggleSelect = useCallback((jobId) => {
        setSelected((prev) =>
            prev.includes(jobId)
                ? prev.filter((id) => id !== jobId)
                : prev.length < 4
                    ? [...prev, jobId]
                    : prev
        );
    }, []);

    const getComparison = useCallback(async () => {
        if (selected.length < 2) return null;
        const result = await compareJobs(selected);
        return result.jobs;
    }, [selected]);

    const filterJobs = useCallback(
        (filterParams) => {
            const { minScore, modality, source, minSalary } = filterParams || {};
            return jobs.filter((j) => {
                // If the filter has a value, check against it.
                if (minScore !== undefined && minScore !== null && minScore > 0 && j.score < minScore) return false;
                if (modality && j.modality !== modality) return false;
                if (source && j.source !== source) return false;
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