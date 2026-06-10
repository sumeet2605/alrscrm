import { apiClient } from "./http";
import type { ApiEnvelope } from "../types/api";
import type { LoginRequest, LoginResponse, TokenPair } from "../types/auth";
import type { User } from "../types/identity";

export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<ApiEnvelope<LoginResponse>>("/auth/login", payload);
  return response.data.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<ApiEnvelope<User>>("/auth/me");
  return response.data.data;
}

export async function refreshToken(refreshToken: string): Promise<TokenPair> {
  const response = await apiClient.post<ApiEnvelope<TokenPair>>("/auth/refresh", {
    refresh_token: refreshToken
  });
  return response.data.data;
}

export async function logout(refreshToken: string): Promise<void> {
  await apiClient.post<ApiEnvelope<Record<string, never>>>("/auth/logout", {
    refresh_token: refreshToken
  });
}
