import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import {
  changePassword as changePasswordRequest,
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest
} from "../api/auth";
import { getApiErrorMessage } from "../api/http";
import type { ChangePasswordRequest, LoginRequest } from "../types/auth";
import type { User } from "../types/identity";
import { clearTokens, getStoredTokens, storeTokens } from "../utils/storage";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  login: (payload: LoginRequest) => Promise<void>;
  changePassword: (payload: ChangePasswordRequest) => Promise<void>;
  logout: () => Promise<void>;
  hasAnyRole: (roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    const tokens = getStoredTokens();
    if (!tokens) {
      setIsBootstrapping(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        clearTokens();
        setUser(null);
      })
      .finally(() => setIsBootstrapping(false));
  }, []);

  const login = useCallback(async (payload: LoginRequest) => {
    try {
      const response = await loginRequest(payload);
      storeTokens({
        accessToken: response.access_token,
        refreshToken: response.refresh_token
      });
      setUser(response.user);
    } catch (error) {
      throw new Error(getApiErrorMessage(error));
    }
  }, []);

  const changePassword = useCallback(async (payload: ChangePasswordRequest) => {
    try {
      const response = await changePasswordRequest(payload);
      storeTokens({
        accessToken: response.access_token,
        refreshToken: response.refresh_token
      });
      setUser(response.user);
    } catch (error) {
      throw new Error(getApiErrorMessage(error));
    }
  }, []);

  const logout = useCallback(async () => {
    const tokens = getStoredTokens();
    if (tokens?.refreshToken) {
      await logoutRequest(tokens.refreshToken).catch(() => undefined);
    }
    clearTokens();
    setUser(null);
  }, []);

  const hasAnyRole = useCallback(
    (roles: string[]) => {
      if (!user) {
        return false;
      }
      return user.roles.some((role) => roles.includes(role.name));
    },
    [user]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isBootstrapping,
      login,
      changePassword,
      logout,
      hasAnyRole
    }),
    [changePassword, hasAnyRole, isBootstrapping, login, logout, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
