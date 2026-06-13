import type { IntegrationProvider, IntegrationStatus } from "../../types/integrations";

export const integrationProviders: IntegrationProvider[] = [
  "WHATSAPP_CLOUD_API",
  "INSTAGRAM_BUSINESS",
  "FACEBOOK_PAGE",
  "SMTP_EMAIL",
  "GOOGLE_CLOUD_STORAGE",
  "AWS_S3"
];

export const integrationStatuses: IntegrationStatus[] = [
  "CONNECTED",
  "DISCONNECTED",
  "EXPIRED",
  "ERROR"
];

export function labelFromEnum(value?: string | null): string {
  if (!value) return "-";
  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function statusColor(status: IntegrationStatus): string {
  const colors: Record<IntegrationStatus, string> = {
    CONNECTED: "success",
    DISCONNECTED: "default",
    EXPIRED: "warning",
    ERROR: "error"
  };
  return colors[status];
}

export function providerFields(provider: IntegrationProvider): string[] {
  const fields: Record<IntegrationProvider, string[]> = {
    WHATSAPP_CLOUD_API: ["access_token", "phone_number_id"],
    INSTAGRAM_BUSINESS: ["access_token", "business_account_id"],
    FACEBOOK_PAGE: ["access_token", "page_id"],
    SMTP_EMAIL: ["host", "port", "username", "password", "from_email"],
    GOOGLE_CLOUD_STORAGE: ["bucket", "credentials_json"],
    AWS_S3: ["bucket", "region", "access_key_id", "secret_access_key"]
  };
  return fields[provider];
}
