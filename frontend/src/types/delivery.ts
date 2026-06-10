import type { PaginationMeta } from "./api";

export type DeliveryStatus =
  | "PENDING"
  | "ZIP_GENERATING"
  | "READY"
  | "SENT"
  | "DELIVERED"
  | "EXPIRED"
  | "REOPEN_REQUESTED"
  | "REOPENED"
  | "CLOSED";

export type ZipGenerationStatus = "PENDING" | "GENERATING" | "COMPLETED" | "FAILED";

export interface DeliveryJob {
  id: string;
  organization_id: string;
  branch_id: string;
  family_id: string;
  booking_id: string;
  gallery_id: string;
  editing_job_id: string;
  delivery_number: string;
  delivery_status: DeliveryStatus;
  edited_photo_count: number;
  delivery_date: string;
  expiry_date: string;
  delivery_link?: string | null;
  download_count: number;
  max_downloads: number;
  allow_re_download: boolean;
  re_download_fee: string;
  watermark_enabled: boolean;
  original_download_enabled: boolean;
  zip_generation_status: ZipGenerationStatus;
  client_notified_at?: string | null;
  last_downloaded_at?: string | null;
  delivery_notes?: string | null;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  family_name?: string | null;
  booking_number?: string | null;
  gallery_name?: string | null;
  service_type?: string | null;
}

export interface ClientDelivery extends DeliveryJob {
  remaining_downloads: number;
}

export interface DeliveryJobPayload {
  editing_job_id: string;
  max_downloads?: number;
  allow_re_download?: boolean;
  re_download_fee?: string;
  watermark_enabled?: boolean;
  original_download_enabled?: boolean;
  delivery_notes?: string | null;
}

export interface DeliveryJobUpdatePayload {
  delivery_status?: DeliveryStatus;
  expiry_date?: string | null;
  delivery_link?: string | null;
  max_downloads?: number;
  allow_re_download?: boolean;
  re_download_fee?: string;
  watermark_enabled?: boolean;
  original_download_enabled?: boolean;
  zip_generation_status?: ZipGenerationStatus;
  delivery_notes?: string | null;
}

export interface DeliveryDownload {
  id: string;
  delivery_job_id: string;
  downloaded_at: string;
  ip_address?: string | null;
  user_agent?: string | null;
}

export interface DeliveryMetrics {
  pending_delivery: number;
  ready_delivery: number;
  delivered: number;
  expired: number;
  reopened: number;
  average_delivery_tat: number;
  downloads_this_month: number;
  re_download_revenue_potential: string;
}

export interface DeliveryListParams {
  page: number;
  page_size: number;
  status?: DeliveryStatus;
  branch_id?: string;
  search?: string;
}

export interface DeliveryListResult {
  items: DeliveryJob[];
  meta: PaginationMeta;
}

