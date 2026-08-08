import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getHistorial } from '../services/historialService';
import './Historial.css';

const Historial = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [filtros, setFiltros] = useState({
    fecha_inicio: '',
    fecha_fin: '',
    categoria: '',
    palabra_clave: ''
  });

  const [resultados, setResultados] = useState(null);
  const [estadisticas, setEstadisticas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBuscar = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await getHistorial(filtros);
      setResultados(data.resultados || []);
      setEstadisticas(data.estadisticas || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error al obtener el historial.');
      setResultados(null);
      setEstadisticas([]);
    } finally {
      setLoading(false);
    }
  };

  const handleLimpiar = () => {
    setFiltros({
      fecha_inicio: '',
      fecha_fin: '',
      categoria: '',
      palabra_clave: ''
    });
    setResultados(null);
    setEstadisticas([]);
    setError(null);
  };

  return (
    <div className="historial-container">
      <header className="historial-header">
        <h2 className="historial-title">Historial de Datos</h2>
        <div className="historial-header-actions">
          <button className="btn-back" onClick={() => navigate('/dashboard')}>
            Volver al Dashboard
          </button>
          <button className="btn-logout" onClick={logout}>
            Cerrar Sesión
          </button>
        </div>
      </header>

      <div className="historial-filter-card">
        <form onSubmit={handleBuscar} className="historial-form">
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="fecha_inicio">Fecha Inicio</label>
              <input
                type="date"
                id="fecha_inicio"
                name="fecha_inicio"
                className="form-control"
                value={filtros.fecha_inicio}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="fecha_fin">Fecha Fin</label>
              <input
                type="date"
                id="fecha_fin"
                name="fecha_fin"
                className="form-control"
                value={filtros.fecha_fin}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="categoria">Categoría</label>
              <select
                id="categoria"
                name="categoria"
                className="form-control"
                value={filtros.categoria}
                onChange={handleChange}
              >
                <option value="">Todas</option>
                <option value="Economia">Economía</option>
                <option value="Clima">Clima</option>
                <option value="Geografia">Geografía</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="palabra_clave">Palabra Clave</label>
              <input
                type="text"
                id="palabra_clave"
                name="palabra_clave"
                className="form-control"
                placeholder="Buscar por palabra clave..."
                value={filtros.palabra_clave}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-limpiar" onClick={handleLimpiar}>
              Limpiar filtros
            </button>
            <button type="submit" className="btn-buscar">
              Buscar
            </button>
          </div>
        </form>
      </div>

      {error && <div className="historial-error">{error}</div>}

      {loading ? (
        <div className="historial-message">Cargando historial...</div>
      ) : resultados !== null && (
        resultados.length === 0 ? (
          <div className="historial-message">
            No se encontraron resultados con esos filtros
          </div>
        ) : (
          <>
            <div className="table-container">
              <table className="historial-table">
                <thead>
                  <tr>
                    <th>Fuente</th>
                    <th>Indicador</th>
                    <th>País</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {resultados.map((item, index) => (
                    <tr key={item.id_dato || index}>
                      <td>{item.fuente}</td>
                      <td>{item.indicador}</td>
                      <td>{item.pais}</td>
                      <td>{typeof item.valor === 'number' ? item.valor.toLocaleString() : item.valor}</td>
                      <td>{item.unidad}</td>
                      <td>{item.fecha_dato}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {estadisticas && estadisticas.length > 0 && (
              <div className="estadisticas-section">
                <h3>Estadísticas</h3>
                <div className="estadisticas-grid">
                  {estadisticas.map((stat, idx) => (
                    <div key={idx} className="estadistica-card">
                      <h4 className="estadistica-title">{stat.unidad}</h4>
                      <div className="estadistica-details">
                        <div className="estadistica-item">
                          <span>Promedio:</span>
                          <span>{typeof stat.promedio === 'number' ? stat.promedio.toLocaleString() : stat.promedio}</span>
                        </div>
                        <div className="estadistica-item">
                          <span>Total:</span>
                          <span>{typeof stat.total === 'number' ? stat.total.toLocaleString() : stat.total}</span>
                        </div>
                        <div className="estadistica-item">
                          <span>Cantidad de registros:</span>
                          <span>{stat.cantidad}</span>
                        </div>
                        {stat.pais_max && (
                          <div className="estadistica-item">
                            <span>Máximo ({stat.pais_max.pais}):</span>
                            <span>{typeof stat.pais_max.valor === 'number' ? stat.pais_max.valor.toLocaleString() : stat.pais_max.valor}</span>
                          </div>
                        )}
                        {stat.pais_min && (
                          <div className="estadistica-item">
                            <span>Mínimo ({stat.pais_min.pais}):</span>
                            <span>{typeof stat.pais_min.valor === 'number' ? stat.pais_min.valor.toLocaleString() : stat.pais_min.valor}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )
      )}
    </div>
  );
};

export default Historial;
