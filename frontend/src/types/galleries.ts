import type { PaginationMeta } from "./api";

export type GalleryStatus =
  | "DRAFT"
  | "UPLOADED"
  | "SELECTION_OPEN"
  | "SELECTION_SUBMITTED"
  | "SELECTION_REOPENED"
  | "SELECTION_CLOSED";

export interface Gallery {
  id: string;
  organization_id: string;
  branch_id: string;
  booking_id: string;
  booking_item_id: string;
  gallery_name: string;
  gallery_status: GalleryStatus;
  created_by_user_id: string;
  expires_at?: string | null;
  created_at: string;
  updated_at: string;
  booking_number?: string | null;
  family_name?: string | null;
  photo_count: number;
  favorite_count: number;
  selection_limit: number;
  selection_count: number;
  selection_locked: boolean;
  selection_submitted_at?: string | null;
  selection_deadline?: string | null;
  allow_download: boolean;
  allow_watermark: boolean;
  reopen_count: number;
}

export interface GalleryPhoto {
  id: string;
  gallery_id: string;
  file_name: string;
  storage_path: string;
  thumbnail_path?: string | null;
  file_size: number;
  image_width: number;
  image_height: number;
  sort_order: number;
  is_active: boolean;
  uploaded_at: string;
}

export interface FavoriteSelection {
  id: string;
  gallery_id: string;
  gallery_photo_id: string;
  selected_by_name: string;
  selected_by_email?: string | null;
  selected_at: string;
  gallery_photo?: GalleryPhoto | null;
}

export interface GalleryDetail extends Gallery {
  photos: GalleryPhoto[];
  favorites: FavoriteSelection[];
}

export interface GalleryPayload {
  booking_id: string;
  booking_item_id: string;
  gallery_name: string;
  gallery_status?: GalleryStatus;
  password?: string | null;
  expires_at?: string | null;
}

export interface GalleryUpdatePayload {
  gallery_name?: string;
  gallery_status?: GalleryStatus;
  password?: string | null;
  expires_at?: string | null;
  selection_limit?: number | null;
  selection_deadline?: string | null;
  allow_download?: boolean | null;
  allow_watermark?: boolean | null;
}

export interface GalleryPhotoPayload {
  file_name: string;
  storage_path: string;
  thumbnail_path?: string | null;
  file_size: number;
  image_width: number;
  image_height: number;
  sort_order?: number;
  is_active?: boolean;
}

export interface FavoritePayload {
  gallery_photo_id: string;
  selected_by_name: string;
  selected_by_email?: string | null;
}

export interface GalleryMetrics {
  total_galleries: number;
  photos_uploaded: number;
  selection_open_galleries: number;
  selection_closed_galleries: number;
  favorite_count: number;
}

export interface GalleryListParams {
  page: number;
  page_size: number;
  branch_id?: string;
  gallery_status?: GalleryStatus;
  search?: string;
}

export interface GalleryListResult {
  items: Gallery[];
  meta: PaginationMeta;
}

export interface GalleryAccessToken {
  access_token?: string | null;
  access_url?: string | null;
  expires_at: string;
  revoked: boolean;
}
