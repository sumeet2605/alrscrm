import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

import { clearTokens, getStoredTokens, storeTokens } from "../utils/storage";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

let refreshPromise: Promise<string | null> | null = null;

export const apiClient = axios.create({
  baseURL: API_BASE_URL
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const tokens = getStoredTokens();
  if (tokens?.accessToken && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${tokens.accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    const accessToken = await refreshAccessToken();
    if (!accessToken) {
      clearTokens();
      return Promise.reject(error);
    }
    originalRequest.headers.Authorization = `Bearer ${accessToken}`;
    return apiClient(originalRequest);
  }
);

async function refreshAccessToken(): Promise<string | null> {
  const tokens = getStoredTokens();
  if (!tokens?.refreshToken) {
    return null;
  }

  refreshPromise ??= axios
    .post(`${API_BASE_URL}/auth/refresh`, { refresh_token: tokens.refreshToken })
    .then((response) => {
      const data = response.data.data as { access_token: string; refresh_token: string };
      storeTokens({ accessToken: data.access_token, refreshToken: data.refresh_token });
      return data.access_token;
    })
    .catch(() => null)
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail ?? error.response?.data?.message;
    if (typeof detail === "string") {
      return detail;
    }
  }
  return "Something went wrong. Please try again.";
}
