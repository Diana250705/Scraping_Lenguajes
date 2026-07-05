import { scrapeJobs, compareJobs, api } from "../services/api";
import { useState } from "react";
import { useJobs } from "../hooks/useJobs";
import { JobCard } from "../components/JobCard";
import { FilterPanel } from "../components/FilterPanel";
import { CompareTable } from "../components/CompareTable";
import { Loader } from "../components/Loader";

const DEFAULT_PROFILE = {
    title: "",
    salary_min: null,
    salary_max: null,
    modality: null,
    location: "Lima",
    experience: 0,
    keywords: [],
};

export function Dashboard() {
    // Hook personalizado con la lógica de ofertas
    const { jobs, loading, error, meta, selected, search, toggleSelect, getComparison, filterJobs } = useJobs();

    // Estados locales para búsqueda, filtros, comparación y exportación
    const [query, setQuery] = useState("");
    const [profile, setProfile] = useState(DEFAULT_PROFILE);
    const [filters, setFilters] = useState({ minScore: 0 });
    const [comparing, setComparing] = useState(false);
    const [compareData, setCompareData] = useState(null);
    const [exportSuccess, setExportSuccess] = useState(false);
    const [exportMessage, setExportMessage] = useState("");
    const [exporting, setExporting] = useState(false);

    // Dispara el scraping y scoring llamando a la función de búsqueda del hook
    const handleSearch = (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        search({ query, location: profile.location, max_pages: 2 }, profile);
    };

    // Obtiene las ofertas seleccionadas para comparación y abre el modal
    const handleCompare = async () => {
        if (selected.length < 2) return alert("Selecciona al menos 2 ofertas para comparar");
        const data = await getComparison();
        setCompareData(data);
        setComparing(true);
    };

    // Envía la solicitud al endpoint /export del backend para guardar las ofertas obtenidas
    const handleExport = async () => {
        if (jobs.length === 0) return alert("Haz una búsqueda primero");
        setExporting(true);
        try {
            const { data } = await api.post("/export", {
                search: { query, location: profile.location, max_pages: 2 },
                profile,
            });
            setExportMessage(data.message || "Exportado correctamente");
            setExportSuccess(true);
        } catch (err) {
            alert("Error al exportar: " + (err.response?.data?.detail || err.message));
        } finally {
            setExporting(false);
        }
    };

    // Genera un archivo SQL con las ofertas y lo descarga
    const handleDownloadSQL = () => {
        const escapeSql = (str) => {
            if (str === null || str === undefined) return "NULL";
            return "'" + String(str).replace(/'/g, "''") + "'";
        };

        const escapeNum = (num) => {
            if (num === null || num === undefined || isNaN(num)) return "NULL";
            return num;
        };

        let sqlContent = `-- Dump de Ofertas Laborales - JobScraper\n`;
        sqlContent += `-- Generado: ${new Date().toLocaleString()}\n\n`;

        sqlContent += `CREATE TABLE IF NOT EXISTS jobs (\n`;
        sqlContent += `    id TEXT PRIMARY KEY,\n`;
        sqlContent += `    source TEXT,\n`;
        sqlContent += `    title TEXT,\n`;
        sqlContent += `    company TEXT,\n`;
        sqlContent += `    location TEXT,\n`;
        sqlContent += `    salary_min INTEGER,\n`;
        sqlContent += `    salary_max INTEGER,\n`;
        sqlContent += `    modality TEXT,\n`;
        sqlContent += `    summary TEXT,\n`;
        sqlContent += `    url TEXT,\n`;
        sqlContent += `    score INTEGER,\n`;
        sqlContent += `    score_breakdown JSONB,\n`;
        sqlContent += `    query TEXT,\n`;
        sqlContent += `    created_at TIMESTAMP DEFAULT NOW()\n`;
        sqlContent += `);\n\n`;

        if (filteredJobs.length > 0) {
            sqlContent += `INSERT INTO jobs (id, source, title, company, location, salary_min, salary_max, modality, summary, url, score, score_breakdown, query) VALUES\n`;

            const rows = filteredJobs.map((job) => {
                const idVal = escapeSql(job.id);
                const sourceVal = escapeSql(job.source);
                const titleVal = escapeSql(job.title);
                const companyVal = escapeSql(job.company);
                const locationVal = escapeSql(job.location);
                const salaryMinVal = escapeNum(job.salary?.min);
                const salaryMaxVal = escapeNum(job.salary?.max);
                const modalityVal = escapeSql(job.modality);
                const summaryVal = escapeSql(job.summary);
                const urlVal = escapeSql(job.url);
                const scoreVal = escapeNum(job.score);
                const breakdownVal = escapeSql(JSON.stringify(job.score_breakdown || {}));
                const queryVal = escapeSql(query);

                return `    (${idVal}, ${sourceVal}, ${titleVal}, ${companyVal}, ${locationVal}, ${salaryMinVal}, ${salaryMaxVal}, ${modalityVal}, ${summaryVal}, ${urlVal}, ${scoreVal}, ${breakdownVal}, ${queryVal})`;
            });

            sqlContent += rows.join(",\n") + "\n";
            sqlContent += `ON CONFLICT (id) DO UPDATE SET\n`;
            sqlContent += `    score = EXCLUDED.score,\n`;
            sqlContent += `    score_breakdown = EXCLUDED.score_breakdown;\n`;
        }

        // Descarga el archivo SQL mediante un elemento temporal 'a'
        const blob = new Blob([sqlContent], { type: "text/plain;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `empleos_exportados_${query.replace(/\s+/g, "_")}.sql`);
        link.style.visibility = "hidden";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Genera un archivo Excel con diseño CSS y lo descarga
    const handleExportExcel = () => {
        const sortedJobs = [...filteredJobs].sort((a, b) => b.score - a.score);

        // Diseña las filas HTML asignando colores al score según el rango obtenido
        const buildRow = (job) => {
            const minSal = job.salary?.min !== null && job.salary?.min !== undefined ? `S/ ${job.salary.min.toLocaleString('es-PE')}` : "No especificado";
            const maxSal = job.salary?.max !== null && job.salary?.max !== undefined ? `S/ ${job.salary.max.toLocaleString('es-PE')}` : "No especificado";

            // Estilos CSS inline para la celda del score
            let scoreStyle = "background-color: #fee2e2; color: #991b1b; font-weight: bold; text-align: center;"; // Rojo (<50)
            if (job.score >= 80) {
                scoreStyle = "background-color: #d1fae5; color: #065f46; font-weight: bold; text-align: center;"; // Verde (>=80)
            } else if (job.score >= 50) {
                scoreStyle = "background-color: #fef3c7; color: #92400e; font-weight: bold; text-align: center;"; // Naranja (>=50)
            }

            return `
                <tr>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: middle;">${job.id}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: middle;">${job.source}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: middle; font-weight: 500;">${job.title || "No especificado"}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: middle;">${job.company || "No especificado"}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: middle;">${job.location || "No especificado"}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: right; vertical-align: middle;">${minSal}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: right; vertical-align: middle;">${maxSal}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: middle;">${job.modality || "No especificado"}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 8px; vertical-align: middle; ${scoreStyle}">${job.score}</td>
                </tr>
            `;
        };

        const rowsHtml = sortedJobs.map(buildRow).join("");

        // Estructura XML/HTML interpretada por Excel
        const excelHtml = `
            <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
            <head>
                <meta charset="utf-8" />
                <!--[if gte mso 9]>
                <xml>
                    <x:ExcelWorkbook>
                        <x:ExcelWorksheets>
                            <x:ExcelWorksheet>
                                <x:Name>Ofertas Laborales</x:Name>
                                <x:WorksheetOptions>
                                    <x:DisplayGridlines/>
                                </x:WorksheetOptions>
                            </x:ExcelWorksheet>
                        </x:ExcelWorksheets>
                    </x:ExcelWorkbook>
                </xml>
                <![endif]-->
                <style>
                    table { border-collapse: collapse; font-family: 'Segoe UI', Calibri, sans-serif; font-size: 11pt; }
                    th { background-color: #6366f1; color: #ffffff; font-weight: bold; border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
                </style>
            </head>
            <body>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Portal</th>
                            <th>Título</th>
                            <th>Empresa</th>
                            <th>Ubicación</th>
                            <th>Sueldo Mínimo</th>
                            <th>Sueldo Máximo</th>
                            <th>Modalidad</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            </body>
            </html>
        `;

        // Descarga del Excel mediante enlace temporal
        const blob = new Blob([excelHtml], { type: "application/vnd.ms-excel;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `empleos_exportados_${query.replace(/\s+/g, "_") || "jobs"}.xls`);
        link.style.visibility = "hidden";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Obtiene la lista final de empleos aplicando filtros
    const filteredJobs = filterJobs(filters);

    return (
        <div className="app-container">
            {/* Cabecera principal con buscador general y selector de ubicación */}
            <header className="dashboard-header">
                <div className="header-content">
                    <h1 className="header-title">JobScraper Perú</h1>
                    <form onSubmit={handleSearch} className="search-form">
                        <input
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Busca: Analista de datos, Desarrollador Python..."
                            className="search-input"
                        />
                        <select
                            value={profile.location}
                            onChange={(e) => setProfile((p) => ({ ...p, location: e.target.value }))}
                            className="search-select"
                        >
                            <option value="Lima">Lima</option>
                            <option value="Arequipa">Arequipa</option>
                            <option value="Cusco">Cusco</option>
                            <option value="Peru">Todo Perú</option>
                        </select>
                        <button type="submit" disabled={loading} className="search-button">
                            {loading ? "Buscando..." : "Buscar"}
                        </button>
                    </form>
                </div>
            </header>

            <div className="dashboard-grid">
                <aside className="sidebar-panel">
                    <FilterPanel
                        profile={profile}
                        onProfileChange={setProfile}
                        onFilterChange={setFilters}
                        sources={meta.sources}
                    />
                </aside>

                <main className="main-content">
                    {loading && <Loader message="Buscando en portales laborales..." />}

                    {error && (
                        <div className="error-alert">
                            <strong>Error:</strong> {error}
                        </div>
                    )}

                    {!loading && jobs.length > 0 && (
                        <>
                            <div className="meta-info-bar">
                                <p className="meta-info-text">
                                    {filteredJobs.length} ofertas en {meta.sources?.join(", ")}
                                </p>
                                <div style={{ display: "flex", gap: "8px" }}>
                                    {selected.length > 0 && (
                                        <button onClick={handleCompare} style={{
                                            padding: "8px 16px", backgroundColor: "#6366f1", color: "#fff",
                                            border: "none", borderRadius: "8px", cursor: "pointer", fontSize: "14px"
                                        }}>
                                            Comparar {selected.length} seleccionadas
                                        </button>
                                    )}
                                    <button
                                        onClick={handleExport}
                                        disabled={exporting}
                                        style={{
                                            padding: "8px 16px",
                                            backgroundColor: exporting ? "#6b7280" : "#10b981",
                                            color: "#fff",
                                            border: "none",
                                            borderRadius: "8px",
                                            cursor: exporting ? "not-allowed" : "pointer",
                                            fontSize: "14px",
                                            opacity: exporting ? 0.7 : 1
                                        }}
                                    >
                                        {exporting ? "Exportando..." : "Exportar"}
                                    </button>
                                </div>
                            </div>

                            <div className="job-grid">
                                {filteredJobs.map((job) => (
                                    <JobCard key={job.id} job={job} isSelected={selected.includes(job.id)} onToggleSelect={toggleSelect} />
                                ))}
                            </div>
                        </>
                    )}

                    {!loading && jobs.length === 0 && !error && (
                        <div style={{ textAlign: "center", padding: "80px 20px", color: "var(--text-muted)" }}>
                            <p style={{ fontSize: "16px", fontWeight: 500, margin: 0 }}>Ingresa un puesto y haz clic en Buscar para empezar.</p>
                        </div>
                    )}
                </main>
            </div>

            {comparing && compareData && (
                <CompareTable jobs={compareData} onClose={() => setComparing(false)} />
            )}

            {exportSuccess && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{ maxWidth: "450px", textAlign: "center" }}>
                        <div style={{ fontSize: "48px", marginBottom: "16px" }}>🎉</div>
                        <h2 className="modal-title" style={{ marginBottom: "12px", display: "block" }}>¡Exportación Exitosa!</h2>
                        <p style={{ color: "var(--text-secondary)", marginBottom: "24px", fontSize: "15px" }}>
                            {exportMessage}
                        </p>
                        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                            <button onClick={handleExportExcel} className="btn-primary" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", padding: "12px", backgroundColor: "#10b981" }}>
                                Exportar en Excel
                            </button>
                            <button onClick={handleDownloadSQL} className="btn-primary" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", padding: "12px" }}>
                                Descargar Tabla (SQL)
                            </button>
                            <button onClick={() => setExportSuccess(false)} className="btn-secondary" style={{ padding: "12px" }}>
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}