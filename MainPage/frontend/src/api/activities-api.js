import { api } from './client';

export const createActivity = async (payload) => {
  const res = await api.post('/activities', payload);
  return res.data;
};

export const nextActivityTurn = async (payload) => {
  const res = await api.post('/activities/next-turn', payload);
  return res.data;
};

export const loadActivityHistory = async () => {
  const res = await api.get('/activities/history');
  return res.data;
};
