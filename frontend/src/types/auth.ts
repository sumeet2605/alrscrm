import type { components } from "./generated/openapi";
import type { User } from "./identity";

export type LoginRequest = components["schemas"]["LoginRequest"];
export type RefreshRequest = components["schemas"]["RefreshRequest"];

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends TokenPair {
  user: User;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}
