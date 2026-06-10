import { apiClient } from "./http";
import type { ApiEnvelope, PaginationMeta } from "../types/api";
import type {
  FollowUp,
  FollowUpPayload,
  FollowUpUpdatePayload,
  LostReason,
  Opportunity,
  OpportunityListParams,
  OpportunityNote,
  OpportunityPayload,
  OpportunityStageHistory,
  OpportunityUpdatePayload,
  Pipeline,
  SalesMetrics
} from "../types/sales";

export interface ListResult<T> {
  items: T[];
  meta: PaginationMeta;
}

export async function listOpportunities(
  params: OpportunityListParams
): Promise<ListResult<Opportunity>> {
  const response = await apiClient.get<ApiEnvelope<Opportunity[]>>("/opportunities", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function getPipeline(): Promise<Pipeline> {
  const response = await apiClient.get<ApiEnvelope<Pipeline>>("/opportunities/pipeline");
  return response.data.data;
}

export async function getSalesMetrics(): Promise<SalesMetrics> {
  const response = await apiClient.get<ApiEnvelope<SalesMetrics>>("/opportunities/metrics");
  return response.data.data;
}

export async function getOpportunity(id: string): Promise<Opportunity> {
  const response = await apiClient.get<ApiEnvelope<Opportunity>>(`/opportunities/${id}`);
  return response.data.data;
}

export async function createOpportunity(payload: OpportunityPayload): Promise<Opportunity> {
  const response = await apiClient.post<ApiEnvelope<Opportunity>>("/opportunities", payload);
  return response.data.data;
}

export async function updateOpportunity(
  id: string,
  payload: OpportunityUpdatePayload
): Promise<Opportunity> {
  const response = await apiClient.put<ApiEnvelope<Opportunity>>(`/opportunities/${id}`, payload);
  return response.data.data;
}

export async function deleteOpportunity(id: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(`/opportunities/${id}`);
}

export async function listFollowUps(params: {
  page?: number;
  page_size?: number;
  status?: string;
  due_from?: string;
  due_to?: string;
}): Promise<ListResult<FollowUp>> {
  const response = await apiClient.get<ApiEnvelope<FollowUp[]>>("/followups", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createFollowUp(payload: FollowUpPayload): Promise<FollowUp> {
  const response = await apiClient.post<ApiEnvelope<FollowUp>>("/followups", payload);
  return response.data.data;
}

export async function updateFollowUp(
  id: string,
  payload: FollowUpUpdatePayload
): Promise<FollowUp> {
  const response = await apiClient.put<ApiEnvelope<FollowUp>>(`/followups/${id}`, payload);
  return response.data.data;
}

export async function listLostReasons(): Promise<LostReason[]> {
  const response = await apiClient.get<ApiEnvelope<LostReason[]>>("/lost-reasons");
  return response.data.data;
}

export async function createOpportunityNote(
  opportunityId: string,
  note: string
): Promise<OpportunityNote> {
  const response = await apiClient.post<ApiEnvelope<OpportunityNote>>(
    `/opportunities/${opportunityId}/notes`,
    { note }
  );
  return response.data.data;
}

export async function listOpportunityNotes(opportunityId: string): Promise<OpportunityNote[]> {
  const response = await apiClient.get<ApiEnvelope<OpportunityNote[]>>(
    `/opportunities/${opportunityId}/notes`
  );
  return response.data.data;
}

export async function listOpportunityHistory(
  opportunityId: string
): Promise<OpportunityStageHistory[]> {
  const response = await apiClient.get<ApiEnvelope<OpportunityStageHistory[]>>(
    `/opportunities/${opportunityId}/history`
  );
  return response.data.data;
}
