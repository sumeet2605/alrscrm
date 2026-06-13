import type { PaginationMeta } from "./api";

export type IntegrationProvider =
  | "WHATSAPP_CLOUD_API"
  | "INSTAGRAM_BUSINESS"
  | "FACEBOOK_PAGE"
  | "SMTP_EMAIL"
  | "GOOGLE_CLOUD_STORAGE"
  | "AWS_S3";

export type IntegrationStatus = "CONNECTED" | "DISCONNECTED" | "EXPIRED" | "ERROR";

export interface Integration {
  id: string;
  organization_id: string;
  branch_id?: string | null;
  provider: IntegrationProvider;
  status: IntegrationStatus;
  last_verified_at?: string | null;
  last_error?: string | null;
  credential_keys: string[];
  created_by_user_id: string;
  updated_by_user_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface IntegrationPayload {
  organization_id: string;
  branch_id?: string | null;
  provider: IntegrationProvider;
  credentials: Record<string, string | number | boolean>;
}

export interface IntegrationUpdatePayload {
  branch_id?: string | null;
  status?: IntegrationStatus;
  credentials?: Record<string, string | number | boolean>;
}

export interface IntegrationListParams {
  page?: number;
  page_size?: number;
  branch_id?: string;
  provider?: IntegrationProvider;
  status?: IntegrationStatus;
}

export interface IntegrationListResult {
  items: Integration[];
  meta: PaginationMeta;
}

export interface IntegrationHealth {
  connected: number;
  disconnected: number;
  expired: number;
  error: number;
}
