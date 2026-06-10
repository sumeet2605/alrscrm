import type { components, paths } from "./generated/openapi";

export interface ApiEnvelope<T> {
  success: components["schemas"]["APIResponse"]["success"];
  message: components["schemas"]["APIResponse"]["message"];
  data: T;
  meta?: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface PaginatedRequest
  extends NonNullable<paths["/api/v1/users"]["get"]["parameters"]["query"]> {
  search?: string;
}
