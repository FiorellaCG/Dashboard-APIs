import React, { useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import widgetService from '../services/widgetService';
import './WidgetCard.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const WidgetCard = ({ widget }) => {
  const [pais, setPais] = useState('');
  const [historialConsultas, setHistorialConsultas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleConsultar = async () => {
    if (!pais.trim()) {
      setError('Por favor, ingresa un país o ciudad.');
      return;
    }
    setLoading(true);
    setError(null);
    
    try {
      const responseData = await widgetService.getDashboardData(widget.id_widget, pais);
      
      const newConsulta = {
        pais: responseData.datos.pais || pais,
        valor: responseData.datos.valor,
        unidad: responseData.datos.unidad,
        fecha_dato: responseData.datos.fecha_dato
      };
      
      setHistorialConsultas(prev => {
        const filtered = prev.filter(item => item.pais.toLowerCase() !== newConsulta.pais.toLowerCase());
        return [...filtered, newConsulta];
      });

    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Error al obtener datos del widget.');
    } finally {
      setLoading(false);
    }
  };

  const renderChart = () => {
    if (historialConsultas.length === 0) return null;
    
    const labels = historialConsultas.map(item => item.pais);
    const dataValues = historialConsultas.map(item => item.valor);
    const unidad = historialConsultas[0].unidad;

    const backgroundColors = [
      '#6366F1', '#818CF8', '#A5B4FC', '#C7D2FE', '#4F46E5', '#4338CA', '#3730A3'
    ];

    const data = {
      labels,
      datasets: [
        {
          label: unidad,
          data: dataValues,
          backgroundColor: widget.tipo_grafico === 'pastel' ? backgroundColors : '#6366F1',
          borderColor: widget.tipo_grafico === 'lineas' ? '#6366F1' : '#FFFFFF',
          borderWidth: 2,
          fill: false,
          tension: 0.1,
        }
      ]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        }
      }
    };

    return (
      <div className="chart-container">
        {widget.tipo_grafico === 'barras' && <Bar data={data} options={options} />}
        {widget.tipo_grafico === 'lineas' && <Line data={data} options={options} />}
        {widget.tipo_grafico === 'pastel' && <Pie data={data} options={options} />}
      </div>
    );
  };

  return (
    <div className="widget-card">
      <h3 className="widget-title">{widget.nombre}</h3>
      <p className="widget-type">
        <strong>Tipo:</strong> {widget.tipo_grafico}
      </p>
      
      <div className="widget-controls">
        <input 
          type="text" 
          className="widget-input"
          value={pais} 
          onChange={(e) => setPais(e.target.value)} 
          placeholder="País o ciudad (Ej. Mexico)" 
        />
        <button 
          className="btn-consultar"
          onClick={handleConsultar} 
          disabled={loading}
        >
          {loading ? 'Cargando...' : 'Consultar'}
        </button>
      </div>

      {error && <div className="widget-error">{error}</div>}
      
      {historialConsultas.length === 0 ? (
        <div className="widget-empty-state">
          <p>Aún no hay datos. Ingresa un país y consulta para ver resultados.</p>
        </div>
      ) : (
        <>
          {renderChart()}
          <div className="widget-history-table">
            <h4>Detalle de consultas</h4>
            <table>
              <thead>
                <tr>
                  <th>País</th>
                  <th>Valor</th>
                  <th>Unidad</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {historialConsultas.map((item, index) => (
                  <tr key={index}>
                    <td>{item.pais}</td>
                    <td>{item.valor}</td>
                    <td>{item.unidad}</td>
                    <td>{item.fecha_dato}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button className="btn-limpiar" onClick={() => setHistorialConsultas([])}>Limpiar</button>
        </>
      )}
    </div>
  );
};

export default WidgetCard;
