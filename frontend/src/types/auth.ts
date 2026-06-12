import type { components } from "./generated/openapi";
import type { User } from "./identity";

export interface LoginRequest {
  organization_code: string;
  email: string;
  password: string;
}
export type RefreshRequest = components["schemas"]["RefreshRequest"];

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends TokenPair {
  user: User;
}

export interface ChangePasswordResponse extends TokenPair {
  user: User;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}
