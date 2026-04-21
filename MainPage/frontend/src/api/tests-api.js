import { api } from './client';

export const generateTest = async (payload) => {
  const res = await api.post('/tests/generate', payload);
  return res.data;
};

export const getTest = async (testId) => {
  const res = await api.get(`/tests/${testId}`);
  return res.data;
};

export const submitTest = async (
  testId,
  payload
) => {
  const res = await api.post(`/tests/${testId}/submit`, payload);
  return res.data;
};

export const getAttemptResult = async (attemptId) => {
  const res = await api.get(`/attempts/${attemptId}/result`);
  return res.data;
};

export const getAttemptReview = async (attemptId) => {
  const res = await api.get(`/attempts/${attemptId}/review`);
  return res.data;
};
