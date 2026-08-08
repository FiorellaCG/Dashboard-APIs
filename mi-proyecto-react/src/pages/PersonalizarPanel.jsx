import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMiPanel, guardarPanel } from '../services/panelService';
import './PersonalizarPanel.css';

const PersonalizarPanel = () => {
  const navigate = useNavigate();
  const [widgets, setWidgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [mensajeStatus, setMensajeStatus] = useState(null); // { type: 'success' | 'error', text: string }

  useEffect(() => {
    const fetchPanel = async () => {
      try {
        const data = await getMiPanel();
        setWidgets(data);
      } catch (err) {
        setError('Error al cargar la configuración de los widgets.');
      } finally {
        setLoading(false);
      }
    };

    fetchPanel();
  }, []);

  const handleVisibleChange = (id_widget, checked) => {
    setWidgets((prev) =>
      prev.map((w) => (w.id_widget === id_widget ? { ...w, visible: checked } : w))
    );
  };

  const handleTipoGraficoChange = (id_widget, nuevoTipo) => {
    setWidgets((prev) =>
      prev.map((w) =>
        w.id_widget === id_widget ? { ...w, tipo_grafico_personalizado: nuevoTipo } : w
      )
    );
  };

  const handleGuardar = async () => {
    setSaving(true);
    setMensajeStatus(null);
    try {
      const payload = widgets.map((w, index) => ({
        id_widget: w.id_widget,
        visible: Boolean(w.visible),
        orden: w.orden ?? index,
        tipo_grafico: w.tipo_grafico_personalizado,
      }));

      await guardarPanel(payload);
      setMensajeStatus({
        type: 'success',
        text: '¡Configuración del panel guardada exitosamente!',
      });
    } catch (err) {
      setMensajeStatus({
        type: 'error',
        text: 'Ocurrió un error al guardar la configuración del panel.',
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="personalizar-container">
      <header className="personalizar-header">
        <h2 className="personalizar-title">Personalizar Mi Panel</h2>
        <button className="btn-volver" onClick={() => navigate('/dashboard')}>
          Volver al Dashboard
        </button>
      </header>

      {loading ? (
        <p className="personalizar-loading">Cargando widgets...</p>
      ) : error ? (
        <p className="personalizar-error-page">{error}</p>
      ) : (
        <div className="personalizar-content">
          {mensajeStatus && (
            <div className={`status-message ${mensajeStatus.type}`}>
              {mensajeStatus.text}
            </div>
          )}

          <div className="widgets-list">
            {widgets.map((widget) => (
              <div key={widget.id_widget} className="widget-row-card">
                <div className="widget-info">
                  <h3 className="widget-name">{widget.nombre}</h3>
                  <p className="widget-original-type">
                    Original: {widget.tipo_grafico_original}
                  </p>
                </div>

                <div className="widget-controls-group">
                  <div className="control-item">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        className="checkbox-input"
                        checked={Boolean(widget.visible)}
                        onChange={(e) =>
                          handleVisibleChange(widget.id_widget, e.target.checked)
                        }
                      />
                      Visible en mi dashboard
                    </label>
                  </div>

                  <div className="control-item">
                    <label htmlFor={`select-tipo-${widget.id_widget}`}>
                      Gráfico:
                    </label>
                    <select
                      id={`select-tipo-${widget.id_widget}`}
                      className="select-input"
                      value={widget.tipo_grafico_personalizado || 'barras'}
                      onChange={(e) =>
                        handleTipoGraficoChange(widget.id_widget, e.target.value)
                      }
                    >
                      <option value="barras">Barras</option>
                      <option value="lineas">Líneas</option>
                      <option value="pastel">Pastel</option>
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="personalizar-actions">
            <button
              className="btn-guardar"
              onClick={handleGuardar}
              disabled={saving}
            >
              {saving ? 'Guardando...' : 'Guardar cambios'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonalizarPanel;
