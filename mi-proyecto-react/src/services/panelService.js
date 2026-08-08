import api from './api';

export const getMiPanel = async () => {
  const response = await api.get('/mi-panel/');
  return response.data;
};

export const guardarPanel = async (widgets) => {
  const response = await api.post('/mi-panel/guardar/', { widgets });
  return response.data;
};

export default {
  getMiPanel,
  guardarPanel
};
