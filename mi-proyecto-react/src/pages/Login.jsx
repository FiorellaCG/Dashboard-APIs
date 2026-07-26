import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // Estado 2FA
  const [mostrando2FA, setMostrando2FA] = useState(false);
  const [correo2FA, setCorreo2FA] = useState('');
  const [codigo2FA, setCodigo2FA] = useState('');

  const { login, verificarCodigo2FA } = useAuth();
  const navigate = useNavigate();

  // ── Paso 1: credenciales normales ─────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await login(correo, password);

      if (data?.requiere_2fa) {
        // El usuario tiene 2FA activado → mostrar segundo formulario
        setCorreo2FA(data.correo || correo);
        setMostrando2FA(true);
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Error al iniciar sesión. Verifica tus credenciales.';
      setError(errorMsg);
    }
  };

  // ── Paso 2: verificar código TOTP ────────────────────────────────────
  const handleVerificar2FA = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await verificarCodigo2FA(correo2FA, codigo2FA);
      navigate('/dashboard');
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Código incorrecto. Intenta de nuevo.';
      setError(errorMsg);
    }
  };

  // ── Render: segundo formulario 2FA ───────────────────────────────────
  if (mostrando2FA) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="two-fa-icon"></div>
          <h2>Verificación en dos pasos</h2>
          <p className="two-fa-hint">
            Ingresa el código de 6 dígitos generado por tu app de autenticación.
          </p>

          {error && <div className="auth-error">{error}</div>}

          <form onSubmit={handleVerificar2FA}>
            <div className="form-group">
              <label>Código de verificación</label>
              <input
                type="text"
                value={codigo2FA}
                onChange={(e) => setCodigo2FA(e.target.value.replace(/\D/g, '').slice(0, 6))}
                required
                placeholder="123456"
                maxLength={6}
                inputMode="numeric"
                autoFocus
                className="input-otp"
              />
            </div>
            <button type="submit" className="auth-button">
              Verificar
            </button>
          </form>

          <p className="auth-footer">
            <button
              className="link-button"
              onClick={() => {
                setMostrando2FA(false);
                setError('');
                setCodigo2FA('');
              }}
            >
              ← Volver al inicio de sesión
            </button>
          </p>
        </div>
      </div>
    );
  }

  // ── Render: formulario de login normal ───────────────────────────────
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Iniciar Sesión</h2>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={handleSubmit}>
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
          <button type="submit" className="auth-button">
            Ingresar
          </button>
        </form>
        <p className="auth-footer">
          ¿No tienes cuenta? <Link to="/registro">Regístrate</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
