import { apiClient } from "./http";
import type { ApiEnvelope } from "../types/api";
import type {
  ClientDelivery,
  DeliveryAuthenticateResponse,
  DeliveryDownload,
  DeliveryDownloadResponse,
  DeliveryJob,
  DeliveryJobPayload,
  DeliveryJobUpdatePayload,
  DeliveryListParams,
  DeliveryListResult,
  DeliveryMetrics,
  DeliveryReopenPayload
} from "../types/delivery";

export async function listDeliveryJobs(params: DeliveryListParams): Promise<DeliveryListResult> {
  const response = await apiClient.get<ApiEnvelope<DeliveryJob[]>>("/delivery/jobs", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createDeliveryJob(payload: DeliveryJobPayload): Promise<DeliveryJob> {
  const response = await apiClient.post<ApiEnvelope<DeliveryJob>>("/delivery/jobs", payload);
  return response.data.data;
}

export async function getDeliveryJob(id: string): Promise<DeliveryJob> {
  const response = await apiClient.get<ApiEnvelope<DeliveryJob>>(`/delivery/jobs/${id}`);
  return response.data.data;
}

export async function updateDeliveryJob(
  id: string,
  payload: DeliveryJobUpdatePayload
): Promise<DeliveryJob> {
  const response = await apiClient.put<ApiEnvelope<DeliveryJob>>(`/delivery/jobs/${id}`, payload);
  return response.data.data;
}

export async function generateDeliveryZip(id: string): Promise<DeliveryJob> {
  const response = await apiClient.post<ApiEnvelope<DeliveryJob>>(
    `/delivery/jobs/${id}/generate-zip`
  );
  return response.data.data;
}

export async function sendDelivery(id: string): Promise<DeliveryJob> {
  const response = await apiClient.post<ApiEnvelope<DeliveryJob>>(`/delivery/jobs/${id}/send`);
  return response.data.data;
}

export async function requestDeliveryReopen(
  token: string,
  payload: DeliveryReopenPayload
): Promise<ClientDelivery> {
  const response = await apiClient.post<ApiEnvelope<ClientDelivery>>(
    `/delivery/client/${token}/reopen-request`,
    payload
  );
  return response.data.data;
}

export async function approveDeliveryReopen(id: string): Promise<DeliveryJob> {
  const response = await apiClient.post<ApiEnvelope<DeliveryJob>>(
    `/delivery/jobs/${id}/approve-reopen`
  );
  return response.data.data;
}

export async function closeDelivery(id: string): Promise<DeliveryJob> {
  const response = await apiClient.post<ApiEnvelope<DeliveryJob>>(`/delivery/jobs/${id}/close`);
  return response.data.data;
}

export async function rotateDeliveryAccessToken(id: string): Promise<DeliveryJob> {
  const response = await apiClient.post<ApiEnvelope<DeliveryJob>>(
    `/delivery/jobs/${id}/access-token/rotate`
  );
  return response.data.data;
}

export async function revokeDeliveryAccessTokens(id: string): Promise<DeliveryJob> {
  const response = await apiClient.post<ApiEnvelope<DeliveryJob>>(
    `/delivery/jobs/${id}/access-token/revoke`
  );
  return response.data.data;
}

export async function listDeliveryDownloads(id: string): Promise<DeliveryDownload[]> {
  const response = await apiClient.get<ApiEnvelope<DeliveryDownload[]>>(
    `/delivery/jobs/${id}/downloads`
  );
  return response.data.data;
}

export async function getDeliveryMetrics(): Promise<DeliveryMetrics> {
  const response = await apiClient.get<ApiEnvelope<DeliveryMetrics>>("/delivery/metrics");
  return response.data.data;
}

export async function getClientDelivery(id: string): Promise<ClientDelivery> {
  const response = await apiClient.get<ApiEnvelope<ClientDelivery>>(`/delivery/client/${id}`);
  return response.data.data;
}

export async function authenticateClientDelivery(
  token: string,
  password?: string
): Promise<DeliveryAuthenticateResponse> {
  const response = await apiClient.post<ApiEnvelope<DeliveryAuthenticateResponse>>(
    "/delivery/public/authenticate",
    { token, password }
  );
  return response.data.data;
}

export async function downloadClientDelivery(
  token: string,
  sessionToken: string
): Promise<DeliveryDownloadResponse> {
  const response = await apiClient.post<ApiEnvelope<DeliveryDownloadResponse>>(
    `/delivery/client/${token}/download`,
    {},
    { headers: { Authorization: `Bearer ${sessionToken}` } }
  );
  return response.data.data;
}
