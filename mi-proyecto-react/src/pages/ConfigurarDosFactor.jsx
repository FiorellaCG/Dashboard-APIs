import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import dosFactorService from '../services/dosFactorService';
import './ConfigurarDosFactor.css';

const ConfigurarDosFactor = () => {
  const navigate = useNavigate();

  const [paso, setPaso] = useState('inicio'); // 'inicio' | 'qr' | 'exito'
  const [qrBase64, setQrBase64] = useState('');
  const [secretoManual, setSecretoManual] = useState('');
  const [codigo, setCodigo] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  // ── Paso 1: solicitar QR al backend ────────────────────────────────
  const handleActivar = async () => {
    setCargando(true);
    setError('');
    try {
      const data = await dosFactorService.activar2FA();
      setQrBase64(data.qr_base64);
      setSecretoManual(data.secreto_manual);
      setPaso('qr');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Error al iniciar la configuración de 2FA.'
      );
    } finally {
      setCargando(false);
    }
  };

  // ── Paso 2: confirmar código TOTP ───────────────────────────────────
  const handleConfirmar = async (e) => {
    e.preventDefault();
    setCargando(true);
    setError('');
    try {
      await dosFactorService.confirmar2FA(codigo);
      setPaso('exito');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Código incorrecto. Intenta de nuevo.'
      );
    } finally {
      setCargando(false);
    }
  };

  // ── Render: paso inicio ─────────────────────────────────────────────
  if (paso === 'inicio') {
    return (
      <div className="twofa-container">
        <div className="twofa-card">
          <div className="twofa-header-icon">🛡️</div>
          <h1>Autenticación en dos pasos</h1>
          <p className="twofa-desc">
            Añade una capa extra de seguridad a tu cuenta vinculando una app
            de autenticación (Google Authenticator, Authy, etc.).
          </p>
          {error && <div className="twofa-error">{error}</div>}
          <button
            className="twofa-btn-primary"
            onClick={handleActivar}
            disabled={cargando}
          >
            {cargando ? 'Generando QR…' : 'Activar 2FA'}
          </button>
          <button className="twofa-btn-link" onClick={() => navigate('/dashboard')}>
            ← Volver al Dashboard
          </button>
        </div>
      </div>
    );
  }

  // ── Render: paso QR ─────────────────────────────────────────────────
  if (paso === 'qr') {
    return (
      <div className="twofa-container">
        <div className="twofa-card twofa-card--wide">
          <div className="twofa-header-icon">📱</div>
          <h1>Configurar 2FA</h1>
          <p className="twofa-desc">
            Ingresa la siguiente clave secreta en tu app de autenticación (Google Authenticator, Authy, etc.):
          </p>

          {/* Secreto manual */}
          <div className="twofa-manual-section">
            <div className="twofa-secret-box">
              <code className="twofa-secret-text">{secretoManual}</code>
              <button
                className="twofa-copy-btn"
                title="Copiar al portapapeles"
                onClick={() => navigator.clipboard.writeText(secretoManual)}
              >
                Copiar
              </button>
            </div>
          </div>

          {/* Formulario de confirmación */}
          <div className="twofa-divider" />
          <p className="twofa-confirm-label">
            Ingresa el código de 6 dígitos que muestra tu app para confirmar:
          </p>

          {error && <div className="twofa-error">{error}</div>}

          <form onSubmit={handleConfirmar} className="twofa-form">
            <input
              type="text"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="123456"
              maxLength={6}
              inputMode="numeric"
              required
              autoFocus
              className="twofa-otp-input"
            />
            <button
              type="submit"
              className="twofa-btn-primary"
              disabled={cargando || codigo.length !== 6}
            >
              {cargando ? 'Verificando…' : 'Confirmar'}
            </button>
          </form>

          <button className="twofa-btn-link" onClick={() => navigate('/dashboard')}>
            Cancelar
          </button>
        </div>
      </div>
    );
  }

  // ── Render: éxito ───────────────────────────────────────────────────
  return (
    <div className="twofa-container">
      <div className="twofa-card">
        <div className="twofa-success-icon">✅</div>
        <h1>2FA activado correctamente</h1>
        <p className="twofa-desc">
          Desde ahora, cada vez que inicies sesión, necesitarás ingresar el
          código de tu app de autenticación.
        </p>
        <button
          className="twofa-btn-primary"
          onClick={() => navigate('/dashboard')}
        >
          Ir al Dashboard
        </button>
      </div>
    </div>
  );
};

export default ConfigurarDosFactor;
