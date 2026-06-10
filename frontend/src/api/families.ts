import { apiClient } from "./http";
import type { ApiEnvelope, PaginationMeta } from "../types/api";
import type {
  Family,
  FamilyListParams,
  FamilyPayload,
  FamilySearchParams,
  FamilyUpdatePayload
} from "../types/families";

export interface FamilyListResult {
  items: Family[];
  meta: PaginationMeta;
}

export async function listFamilies(params: FamilyListParams): Promise<FamilyListResult> {
  const response = await apiClient.get<ApiEnvelope<Family[]>>("/families", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function searchFamilies(params: FamilySearchParams): Promise<FamilyListResult> {
  const response = await apiClient.get<ApiEnvelope<Family[]>>("/families/search", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function getFamily(id: string): Promise<Family> {
  const response = await apiClient.get<ApiEnvelope<Family>>(`/families/${id}`);
  return response.data.data;
}

export async function createFamily(payload: FamilyPayload): Promise<Family> {
  const response = await apiClient.post<ApiEnvelope<Family>>("/families", payload);
  return response.data.data;
}

export async function updateFamily(id: string, payload: FamilyUpdatePayload): Promise<Family> {
  const response = await apiClient.put<ApiEnvelope<Family>>(`/families/${id}`, payload);
  return response.data.data;
}

export async function deleteFamily(id: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(`/families/${id}`);
}
