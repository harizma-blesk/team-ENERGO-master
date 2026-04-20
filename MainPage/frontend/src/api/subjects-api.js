import { api } from './client';

export const loadSubjects = async (params = {}) => {
  const res = await api.get('/subjects', { params });
  return res.data;
};
