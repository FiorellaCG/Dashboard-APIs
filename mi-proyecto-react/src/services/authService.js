import api from './api';

const guardarTokens = (data) => {
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  localStorage.setItem('usuario', JSON.stringify(data.usuario));
};

const login = async (correo, password) => {
  const response = await api.post('/login/', { correo, password });
  const data = response.data;

  // Si el backend pide 2FA, NO guardamos tokens aún
  if (data?.requiere_2fa) {
    return data; // { requiere_2fa: true, correo }
  }

  // Login normal: guardar tokens
  if (data?.access) {
    guardarTokens(data);
  }
  return data;
};

const verificarCodigo2FA = async (correo, codigo) => {
  const response = await api.post('/login/verificar-2fa/', { correo, codigo });
  const data = response.data;
  if (data?.access) {
    guardarTokens(data);
  }
  return data;
};

const registro = async (datos) => {
  const response = await api.post('/registro/', datos);
  if (response.data) {
    guardarTokens(response.data);
  }
  return response.data;
};

const logout = () => {
  localStorage.clear();
};

const getUsuarioActual = () => {
  const usuario = localStorage.getItem('usuario');
  return usuario ? JSON.parse(usuario) : null;
};

export default {
  login,
  verificarCodigo2FA,
  registro,
  logout,
  getUsuarioActual,
};
