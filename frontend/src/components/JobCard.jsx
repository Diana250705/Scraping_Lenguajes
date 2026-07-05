// Componente para tarjeta individual con información clave de una oferta
export function JobCard({ job, isSelected, onToggleSelect }) {
    // Color del badge según el puntaje (verde/ámbar/rojo)
    const scoreColor =
        job.score >= 70 ? "#22c55e" :
            job.score >= 45 ? "#f59e0b" : "#ef4444";

    // Formato legible al rango salarial
    const salary = job.salary;
    const salaryText = salary?.min
        ? `S/ ${salary.min.toLocaleString()}${salary.max ? ` – ${salary.max.toLocaleString()}` : "+"}`
        : "No especificado";

    return (
        <div className={`job-card ${isSelected ? "selected" : ""}`}>
            {/* Origen del portal y puntaje obtenido */}
            <div className="job-card-header">
                <span className="job-source">{job.source}</span>
                <span className="job-score-badge" style={{ color: scoreColor }}>{job.score}/100</span>
            </div>

            <h3 className="job-title">{job.title || "Sin título"}</h3>
            <p className="job-company">{job.company || "Empresa no especificada"}</p>

            {/* Etiquetas rápidas de ubicación, modalidad y sueldo */}
            <div className="job-tags">
                {[job.location, job.modality, salaryText].map((tag, i) => (
                    <span key={i} className="job-tag">{tag}</span>
                ))}
            </div>

            {/* Resumen de la descripción de la vacante */}
            {job.summary && (
                <p className="job-summary">
                    {job.summary.slice(0, 150)}...
                </p>
            )}

            {/* Acciones: abrir enlace externo o seleccionar para comparar */}
            <div className="job-actions">
                <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary"
                >
                    Ver oferta
                </a>
                <button
                    onClick={() => onToggleSelect(job.id)}
                    className={`btn-secondary ${isSelected ? "selected" : ""}`}
                >
                    {isSelected ? "✓ Seleccionada" : "Comparar"}
                </button>
            </div>
        </div>
    );
}