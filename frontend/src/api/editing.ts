import { apiClient } from "./http";
import type { ApiEnvelope } from "../types/api";
import type {
  EditingAssignPayload,
  EditorDashboard,
  EditingJob,
  EditingJobPayload,
  EditingJobUpdatePayload,
  EditingListParams,
  EditingListResult,
  EditingMetrics,
  EditingReviewPayload
} from "../types/editing";

export async function listEditingJobs(params: EditingListParams): Promise<EditingListResult> {
  const response = await apiClient.get<ApiEnvelope<EditingJob[]>>("/editing/jobs", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createEditingJob(payload: EditingJobPayload): Promise<EditingJob> {
  const response = await apiClient.post<ApiEnvelope<EditingJob>>("/editing/jobs", payload);
  return response.data.data;
}

export async function getEditingJob(id: string): Promise<EditingJob> {
  const response = await apiClient.get<ApiEnvelope<EditingJob>>(`/editing/jobs/${id}`);
  return response.data.data;
}

export async function updateEditingJob(
  id: string,
  payload: EditingJobUpdatePayload
): Promise<EditingJob> {
  const response = await apiClient.put<ApiEnvelope<EditingJob>>(`/editing/jobs/${id}`, payload);
  return response.data.data;
}

export async function assignEditingJob(
  id: string,
  payload: EditingAssignPayload
): Promise<EditingJob> {
  const response = await apiClient.post<ApiEnvelope<EditingJob>>(
    `/editing/jobs/${id}/assign-editor`,
    payload
  );
  return response.data.data;
}

export async function startEditingJob(id: string): Promise<EditingJob> {
  const response = await apiClient.post<ApiEnvelope<EditingJob>>(`/editing/jobs/${id}/start`);
  return response.data.data;
}

export async function submitEditingReview(id: string): Promise<EditingJob> {
  const response = await apiClient.post<ApiEnvelope<EditingJob>>(
    `/editing/jobs/${id}/submit-review`
  );
  return response.data.data;
}

export async function approveEditingJob(
  id: string,
  payload: EditingReviewPayload
): Promise<EditingJob> {
  const response = await apiClient.post<ApiEnvelope<EditingJob>>(
    `/editing/jobs/${id}/approve`,
    payload
  );
  return response.data.data;
}

export async function rejectEditingJob(
  id: string,
  payload: EditingReviewPayload
): Promise<EditingJob> {
  const response = await apiClient.post<ApiEnvelope<EditingJob>>(
    `/editing/jobs/${id}/reject`,
    payload
  );
  return response.data.data;
}

export async function markEditingReadyForDelivery(id: string): Promise<EditingJob> {
  const response = await apiClient.post<ApiEnvelope<EditingJob>>(
    `/editing/jobs/${id}/ready-for-delivery`
  );
  return response.data.data;
}

export async function getEditingMetrics(): Promise<EditingMetrics> {
  const response = await apiClient.get<ApiEnvelope<EditingMetrics>>("/editing/metrics");
  return response.data.data;
}

export async function getEditorDashboard(): Promise<EditorDashboard> {
  const response = await apiClient.get<ApiEnvelope<EditorDashboard>>("/editing/my-work");
  return response.data.data;
}
