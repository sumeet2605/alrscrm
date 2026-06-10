import type { PaginationMeta } from "./api";

export type EditingPriority = "LOW" | "NORMAL" | "HIGH" | "URGENT";
export type EditingStatus =
  | "PENDING"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "READY_FOR_REVIEW"
  | "APPROVED"
  | "REJECTED"
  | "READY_FOR_DELIVERY";

export interface EditingUserSummary {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface EditingReview {
  id: string;
  editing_job_id: string;
  reviewed_by_user_id: string;
  review_status: "APPROVED" | "REJECTED";
  review_notes?: string | null;
  reviewed_at: string;
  reviewed_by_user?: EditingUserSummary | null;
}

export interface EditingJob {
  id: string;
  organization_id: string;
  branch_id: string;
  booking_id: string;
  booking_item_id: string;
  gallery_id: string;
  assigned_editor_id?: string | null;
  priority: EditingPriority;
  editing_status: EditingStatus;
  selected_photo_count: number;
  completed_photo_count: number;
  due_date: string;
  started_at?: string | null;
  completed_at?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  assigned_editor?: EditingUserSummary | null;
  reviews: EditingReview[];
  gallery_name?: string | null;
  booking_number?: string | null;
  family_name?: string | null;
  service_type?: string | null;
}

export interface EditingJobPayload {
  gallery_id: string;
  priority?: EditingPriority;
  due_date?: string | null;
  assigned_editor_id?: string | null;
  notes?: string | null;
}

export interface EditingJobUpdatePayload {
  priority?: EditingPriority;
  editing_status?: EditingStatus;
  completed_photo_count?: number;
  due_date?: string | null;
  notes?: string | null;
}

export interface EditingAssignPayload {
  assigned_editor_id: string;
  due_date?: string | null;
}

export interface EditingReviewPayload {
  review_notes?: string | null;
}

export interface EditingMetrics {
  pending_jobs: number;
  assigned_jobs: number;
  in_progress_jobs: number;
  ready_for_review: number;
  ready_for_delivery: number;
  overdue_jobs: number;
  average_editing_tat: number;
  average_review_tat: number;
  jobs_by_editor: Record<string, number>;
  jobs_by_priority: Record<string, number>;
  jobs_by_service_type: Record<string, number>;
  photos_edited_this_month: number;
}

export interface EditorDashboard {
  assigned_jobs: number;
  due_today: number;
  overdue: number;
  completed_this_week: number;
  current_workload: number;
}

export interface EditingListParams {
  page: number;
  page_size: number;
  status?: EditingStatus;
  priority?: EditingPriority;
  assigned_editor_id?: string;
  branch_id?: string;
}

export interface EditingListResult {
  items: EditingJob[];
  meta: PaginationMeta;
}
