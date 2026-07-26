import api from './api';

const activar2FA = async () => {
  const response = await api.post('/2fa/activar/');
  return response.data; // { qr_base64, secreto_manual }
};

const confirmar2FA = async (codigo) => {
  const response = await api.post('/2fa/confirmar/', { codigo });
  return response.data;
};

export default {
  activar2FA,
  confirmar2FA,
};
