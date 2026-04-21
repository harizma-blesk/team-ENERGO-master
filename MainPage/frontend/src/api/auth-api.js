import { api } from './client';
import { setStoredTokens } from '../store/auth-storage';

export const registerRequest = async (payload) => {
  const res = await api.post('/auth/register', payload);
  const { accessToken } = res.data.tokens;
  setStoredTokens({ accessToken });
  return res.data;
};

export const loginRequest = async (payload) => {
  const res = await api.post('/auth/login', payload);
  const { accessToken } = res.data.tokens;
  setStoredTokens({ accessToken });
  return res.data;
};

export const meRequest = async () => {
  const res = await api.get('/auth/me');
  return res.data;
};

export const logoutRequest = async () => {
  await api.post('/auth/logout', {});
  setStoredTokens(null);
};
