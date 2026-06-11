import { apiClient } from "./http";
import type { ApiEnvelope, PaginationMeta } from "../types/api";
import type {
  Branch,
  BranchListParams,
  BranchPayload,
  BranchUpdatePayload,
  Organization,
  OrganizationListParams,
  OrganizationOnboardingPayload,
  OrganizationOnboardingResult,
  OrganizationPayload,
  OrganizationSettings,
  OrganizationSettingsUpdatePayload,
  OrganizationUpdatePayload,
  Role,
  User,
  UserListParams,
  UserPayload,
  UserUpdatePayload
} from "../types/identity";

export interface ListResult<T> {
  items: T[];
  meta: PaginationMeta;
}

function buildParams(
  params: BranchListParams | UserListParams | OrganizationListParams
): Record<string, string | number> {
  return {
    page: params.page ?? 1,
    page_size: params.page_size ?? 10
  };
}

export async function listOrganizations(
  params: OrganizationListParams
): Promise<ListResult<Organization>> {
  const response = await apiClient.get<ApiEnvelope<Organization[]>>("/organizations", {
    params: buildParams(params)
  });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createOrganization(payload: OrganizationPayload): Promise<Organization> {
  const response = await apiClient.post<ApiEnvelope<Organization>>("/organizations", payload);
  return response.data.data;
}

export async function onboardOrganization(
  payload: OrganizationOnboardingPayload
): Promise<OrganizationOnboardingResult> {
  const response = await apiClient.post<ApiEnvelope<OrganizationOnboardingResult>>(
    "/organizations/onboard",
    payload
  );
  return response.data.data;
}

export async function getOrganization(id: string): Promise<Organization> {
  const response = await apiClient.get<ApiEnvelope<Organization>>(`/organizations/${id}`);
  return response.data.data;
}

export async function updateOrganization(
  id: string,
  payload: OrganizationUpdatePayload
): Promise<Organization> {
  const response = await apiClient.patch<ApiEnvelope<Organization>>(
    `/organizations/${id}`,
    payload
  );
  return response.data.data;
}

export async function activateOrganization(id: string): Promise<Organization> {
  const response = await apiClient.post<ApiEnvelope<Organization>>(
    `/organizations/${id}/activate`
  );
  return response.data.data;
}

export async function deactivateOrganization(id: string): Promise<void> {
  await apiClient.post<ApiEnvelope<Record<string, never>>>(`/organizations/${id}/deactivate`);
}

export async function getOrganizationSettings(id: string): Promise<OrganizationSettings> {
  const response = await apiClient.get<ApiEnvelope<OrganizationSettings>>(
    `/organizations/${id}/settings`
  );
  return response.data.data;
}

export async function updateOrganizationSettings(
  id: string,
  payload: OrganizationSettingsUpdatePayload
): Promise<OrganizationSettings> {
  const response = await apiClient.patch<ApiEnvelope<OrganizationSettings>>(
    `/organizations/${id}/settings`,
    payload
  );
  return response.data.data;
}

export async function listBranches(params: BranchListParams): Promise<ListResult<Branch>> {
  const response = await apiClient.get<ApiEnvelope<Branch[]>>("/branches", {
    params: buildParams(params)
  });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createBranch(payload: BranchPayload): Promise<Branch> {
  const response = await apiClient.post<ApiEnvelope<Branch>>("/branches", payload);
  return response.data.data;
}

export async function updateBranch(id: string, payload: BranchUpdatePayload): Promise<Branch> {
  const response = await apiClient.patch<ApiEnvelope<Branch>>(`/branches/${id}`, payload);
  return response.data.data;
}

export async function deactivateBranch(id: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(`/branches/${id}`);
}

export async function listUsers(params: UserListParams): Promise<ListResult<User>> {
  const response = await apiClient.get<ApiEnvelope<User[]>>("/users", {
    params: buildParams(params)
  });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createUser(payload: UserPayload): Promise<User> {
  const response = await apiClient.post<ApiEnvelope<User>>("/users", payload);
  return response.data.data;
}

export async function updateUser(id: string, payload: UserUpdatePayload): Promise<User> {
  const response = await apiClient.patch<ApiEnvelope<User>>(`/users/${id}`, payload);
  return response.data.data;
}

export async function deactivateUser(id: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(`/users/${id}`);
}

export async function listRoles(): Promise<Role[]> {
  const response = await apiClient.get<ApiEnvelope<Role[]>>("/roles");
  return response.data.data;
}
