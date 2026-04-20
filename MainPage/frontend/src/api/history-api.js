import { api } from './client';

export const loadHistory = async (params) => {
  const res = await api.get('/history/attempts', { params });
  return res.data;
};

export const loadHistoryDetails = async (attemptId) => {
  const res = await api.get(`/history/attempts/${attemptId}`);
  return res.data;
};
