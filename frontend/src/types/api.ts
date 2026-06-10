import type { components } from "./generated/openapi";

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
