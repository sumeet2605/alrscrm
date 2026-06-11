import { apiClient } from "./http";
import type { ApiEnvelope } from "../types/api";
import type {
  Integration,
  IntegrationHealth,
  IntegrationListParams,
  IntegrationListResult,
  IntegrationPayload,
  IntegrationUpdatePayload
} from "../types/integrations";

export async function listIntegrations(
  params: IntegrationListParams = {}
): Promise<IntegrationListResult> {
  const response = await apiClient.get<ApiEnvelope<Integration[]>>("/integrations", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function getIntegrationHealth(): Promise<IntegrationHealth> {
  const response = await apiClient.get<ApiEnvelope<IntegrationHealth>>("/integrations/health");
  return response.data.data;
}

export async function createIntegration(payload: IntegrationPayload): Promise<Integration> {
  const response = await apiClient.post<ApiEnvelope<Integration>>("/integrations", payload);
  return response.data.data;
}

export async function updateIntegration(
  id: string,
  payload: IntegrationUpdatePayload
): Promise<Integration> {
  const response = await apiClient.patch<ApiEnvelope<Integration>>(`/integrations/${id}`, payload);
  return response.data.data;
}

export async function verifyIntegration(id: string): Promise<Integration> {
  const response = await apiClient.post<ApiEnvelope<Integration>>(`/integrations/${id}/verify`);
  return response.data.data;
}
