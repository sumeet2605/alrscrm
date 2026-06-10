import type { User } from "./identity";

export interface LoginRequest {
  email: string;
  password: string;
}

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
