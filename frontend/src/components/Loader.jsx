// Componente visual con animación de carga (spinner) y texto opcional
export function Loader({ message = "Cargando..." }) {
    return (
        <div className="loader-container">
            <div className="spinner" />
            <p className="loader-text">{message}</p>
        </div>
    );
}