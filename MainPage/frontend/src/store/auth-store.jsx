import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { loginRequest, logoutRequest, meRequest, registerRequest } from '../api/auth-api';
import { setStoredTokens } from './auth-storage';

const AuthContext = createContext(undefined);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const reloadUser = useCallback(async () => {
    try {
      const me = await meRequest();
      setUser(me);
    } catch {
      setUser(null);
      setStoredTokens(null);
    }
  }, []);

  useEffect(() => {
    // Always try restoring session: access token may expire but refresh cookie can re-auth.
    reloadUser().finally(() => setIsLoading(false));
  }, [reloadUser]);

  const login = useCallback(async (email, password) => {
    await loginRequest({ email, password });
    await reloadUser();
  }, [reloadUser]);

  const register = useCallback(
    async (payload) => {
      await registerRequest(payload);
      await reloadUser();
    },
    [reloadUser]
  );

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      setStoredTokens(null);
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      login,
      register,
      logout
    }),
    [user, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
};
