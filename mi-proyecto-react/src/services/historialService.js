import api from './api';

export const getHistorial = async (filtros = {}) => {
  const params = new URLSearchParams();

  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  });

  const response = await api.get('/historial/', { params });
  return response.data;
};

export default {
  getHistorial,
};
