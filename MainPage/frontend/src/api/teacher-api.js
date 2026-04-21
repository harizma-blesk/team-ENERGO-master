import { api } from './client';

export const loadTeacherSummary = async (params) => {
  const res = await api.get('/teacher/analytics/summary', { params });
  return res.data;
};

export const loadWeakTopics = async (params) => {
  const res = await api.get('/teacher/analytics/weak-topics', { params });
  return res.data;
};

export const loadTeacherActivities = async (params) => {
  const res = await api.get('/teacher/activities', { params });
  return res.data;
};
