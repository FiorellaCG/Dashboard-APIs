import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getMiPanel } from '../services/panelService';
import WidgetCard from '../components/WidgetCard';
import './Dashboard.css';

const Dashboard = () => {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();
  const [widgets, setWidgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWidgets = async () => {
      try {
        const data = await getMiPanel();
        // Filtrar visibles y ordenar por 'orden' (ascendente)
        const visibleWidgets = data
          .filter((w) => w.visible === true)
          .sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0));
        
        setWidgets(visibleWidgets);
      } catch (err) {
        setError('Error al cargar los widgets disponibles.');
      } finally {
        setLoading(false);
      }
    };

    fetchWidgets();
  }, []);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h2 className="dashboard-title">Dashboard - Bienvenido {usuario?.nombre || usuario?.correo || 'Usuario'}</h2>
        <div className="dashboard-header-actions">
          <button className="btn-2fa" onClick={() => navigate('/personalizar')}>
            Personalizar Panel
          </button>
          <button className="btn-2fa" onClick={() => navigate('/historial')}>
            Ver Histórico
          </button>
          <button className="btn-2fa" onClick={() => navigate('/2fa/configurar')}>
            Configurar 2FA
          </button>
          <button className="btn-logout" onClick={logout}>
            Cerrar Sesión
          </button>
        </div>
      </header>

      {loading ? (
        <p className="dashboard-message">Cargando widgets...</p>
      ) : error ? (
        <p className="dashboard-error">{error}</p>
      ) : widgets.length === 0 ? (
        <p className="dashboard-message">No hay widgets disponibles.</p>
      ) : (
        <div className="widgets-grid">
          {widgets.map((widget) => {
            // Mapear widget para que tipo_grafico sea tipo_grafico_personalizado
            const widgetFormatted = {
              ...widget,
              tipo_grafico: widget.tipo_grafico_personalizado || widget.tipo_grafico_original
            };
            return (
              <WidgetCard key={widgetFormatted.id_widget || widgetFormatted.id} widget={widgetFormatted} />
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
