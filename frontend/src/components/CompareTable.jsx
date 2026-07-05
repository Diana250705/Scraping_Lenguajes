// Componente modal que muestra una tabla comparativa para las ofertas seleccionadas
export function CompareTable({ jobs, onClose }) {
    // Definición de los campos a comparar
    const fields = [
        { label: "Fuente", key: "source" },
        { label: "Empresa", key: "company" },
        { label: "Ubicación", key: "location" },
        { label: "Modalidad", key: "modality" },
        { label: "Score", key: "score" },
    ];

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                {/* Cabecera del modal con botón de cierre */}
                <div className="modal-header">
                    <h2 className="modal-title">Comparar ofertas</h2>
                    <button onClick={onClose} className="modal-close-btn">✕</button>
                </div>

                {/* Contenedor responsivo para la tabla de comparación */}
                <div className="table-responsive">
                    <table className="compare-table">
                        <thead>
                            <tr>
                                <th className="compare-field-label">Campo</th>
                                {/* Genera una columna por cada empleo */}
                                {jobs.map((job) => (
                                    <th key={job.id}>
                                        {job.title || "Sin título"}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {/* Renderiza las celdas para cada campo */}
                            {fields.map((field) => (
                                <tr key={field.key}>
                                    <td className="compare-field-label">
                                        {field.label}
                                    </td>
                                    {jobs.map((job) => (
                                        <td key={job.id}>
                                            {/* Formato badge con colores para el score */}
                                            {field.key === "score" ? (
                                                <span style={{
                                                    fontWeight: 700,
                                                    color: job.score >= 70 ? "#22c55e" : job.score >= 45 ? "#f59e0b" : "#ef4444"
                                                }}>
                                                    {job.score}/100
                                                </span>
                                            ) : (
                                                job[field.key] || "—"
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                            {/* Fila adicional con enlaces */}
                            <tr>
                                <td className="compare-field-label">Enlace</td>
                                {jobs.map((job) => (
                                    <td key={job.id}>
                                        <a href={job.url} target="_blank" rel="noopener noreferrer" className="compare-link">
                                            Ver oferta
                                        </a>
                                    </td>
                                ))}
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}