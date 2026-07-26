import api from './api';

const getWidgets = async () => {
  const response = await api.get('/widgets/');
  return response.data;
};

const getDashboardData = async (idWidget, pais) => {
  const response = await api.get(`/dashboard/${idWidget}/`, {
    params: { pais }
  });
  return response.data;
};

export default {
  getWidgets,
  getDashboardData
};
