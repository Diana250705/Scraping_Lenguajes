import { useState } from "react";

export function FilterPanel({ profile, onProfileChange, onFilterChange, sources = [] }) {
    const [scoreVal, setScoreVal] = useState(0);
    const update = (key, val) => onProfileChange((p) => ({ ...p, [key]: val }));

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <h2 className="panel-title">Mi perfil</h2>

            <label className="filter-label">Puesto buscado
                <input className="filter-input" type="text" value={profile.title}
                    onChange={(e) => update("title", e.target.value)} placeholder="Ej: Data Analyst" />
            </label>

            <label className="filter-label">Sueldo mínimo (S/)
                <input className="filter-input" type="number" value={profile.salary_min || ""}
                    onChange={(e) => update("salary_min", Number(e.target.value))} placeholder="2000" />
            </label>

            <label className="filter-label">Sueldo máximo (S/)
                <input className="filter-input" type="number" value={profile.salary_max || ""}
                    onChange={(e) => update("salary_max", Number(e.target.value))} placeholder="6000" />
            </label>

            <label className="filter-label">Modalidad
                <select className="filter-select" value={profile.modality || ""}
                    onChange={(e) => update("modality", e.target.value || null)}>
                    <option value="">Cualquiera</option>
                    <option value="remoto">Remoto</option>
                    <option value="híbrido">Híbrido</option>
                    <option value="presencial">Presencial</option>
                </select>
            </label>

            <label className="filter-label">Habilidades (separadas por coma)
                <input className="filter-input" type="text"
                    value={profile.keywords.join(", ")}
                    onChange={(e) => update("keywords", e.target.value.split(",").map((k) => k.trim()).filter(Boolean))}
                    placeholder="python, sql, excel" />
            </label>

            <hr className="filter-divider" />
            <h2 className="panel-title">Filtros</h2>

            <label className="filter-label">Score mínimo
                <div className="range-container">
                    <input type="range" min="0" max="100" step="5"
                        className="range-slider"
                        value={scoreVal}
                        onChange={(e) => {
                            const val = Number(e.target.value);
                            setScoreVal(val);
                            onFilterChange({ minScore: val });
                        }} />
                    <span className="range-value">{scoreVal}</span>
                </div>
            </label>

            {sources.length > 0 && (
                <label className="filter-label">Portal
                    <select className="filter-select"
                        onChange={(e) => onFilterChange({ source: e.target.value || undefined })}>
                        <option value="">Todos</option>
                        {sources.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                </label>
            )}
        </div>
    );
}