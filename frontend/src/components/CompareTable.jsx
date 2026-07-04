export function CompareTable({ jobs, onClose }) {
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
                <div className="modal-header">
                    <h2 className="modal-title">Comparar ofertas</h2>
                    <button onClick={onClose} className="modal-close-btn">✕</button>
                </div>

                <div className="table-responsive">
                    <table className="compare-table">
                        <thead>
                            <tr>
                                <th className="compare-field-label">Campo</th>
                                {jobs.map((job) => (
                                    <th key={job.id}>
                                        {job.title || "Sin título"}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {fields.map((field) => (
                                <tr key={field.key}>
                                    <td className="compare-field-label">
                                        {field.label}
                                    </td>
                                    {jobs.map((job) => (
                                        <td key={job.id}>
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