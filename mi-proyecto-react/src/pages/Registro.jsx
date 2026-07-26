import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';
import './Registro.css';

const Registro = () => {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await authService.registro({ nombre, apellido, correo, password });
      // Usar window.location.href en lugar de navigate forza una recarga,
      // esto permite que el AuthContext lea el token del localStorage e inicie sesión correctamente.
      window.location.href = '/dashboard';
    } catch (err) {
      let errorMsg = 'Error al registrar usuario. Intenta de nuevo.';
      const data = err.response?.data;
      if (data) {
        if (data.detail || data.error) {
          errorMsg = data.detail || data.error;
        } else if (typeof data === 'object') {
          // Extrae mensajes de validación de DRF (ej. correo ya existe)
          errorMsg = Object.values(data).flat().join(', ');
        }
      }
      setError(errorMsg);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Crear Cuenta</h2>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nombre</label>
            <input 
              type="text" 
              value={nombre} 
              onChange={(e) => setNombre(e.target.value)} 
              required 
              placeholder="Ej. Juan"
            />
          </div>
          <div className="form-group">
            <label>Apellido</label>
            <input 
              type="text" 
              value={apellido} 
              onChange={(e) => setApellido(e.target.value)} 
              required 
              placeholder="Ej. Pérez"
            />
          </div>
          <div className="form-group">
            <label>Correo Electrónico</label>
            <input 
              type="email" 
              value={correo} 
              onChange={(e) => setCorreo(e.target.value)} 
              required 
              placeholder="tu@correo.com"
            />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              placeholder="••••••••"
            />
          </div>
          <button type="submit" className="auth-button">Registrarse</button>
        </form>
        <p className="auth-footer">
          ¿Ya tienes cuenta? <Link to="/login">Inicia Sesión</Link>
        </p>
      </div>
    </div>
  );
};

export default Registro;
