import { apiClient } from "./http";
import type { ApiEnvelope, PaginationMeta } from "../types/api";
import type {
  Branch,
  BranchListParams,
  BranchPayload,
  BranchUpdatePayload,
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

function buildParams(params: BranchListParams | UserListParams): Record<string, string | number> {
  return {
    page: params.page ?? 1,
    page_size: params.page_size ?? 10
  };
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
