import type { components, paths } from "./generated/openapi";
import type { OpportunityStage, OpportunityType } from "./sales";

export type ServiceType = components["schemas"]["ServiceType"];
export type BookingStatus = components["schemas"]["BookingStatus"];
export type ShootStatus = components["schemas"]["ShootStatus"];
export type AssignmentRole = components["schemas"]["AssignmentRole"];
export type BookingPayload = components["schemas"]["BookingCreate"];
export type BookingUpdatePayload = components["schemas"]["BookingUpdate"];
export type PackagePayload = components["schemas"]["PackageCreate"];
export type PackageUpdatePayload = components["schemas"]["PackageUpdate"];
export type AddonPayload = components["schemas"]["PackageAddonCreate"];
export type AddonUpdatePayload = components["schemas"]["PackageAddonUpdate"];
export type SchedulePayload = components["schemas"]["ShootScheduleCreate"];
export type ScheduleUpdatePayload = components["schemas"]["ShootScheduleUpdate"];
export type AssignmentPayload = components["schemas"]["PhotographerAssignmentCreate"];
export type BookingListParams =
  NonNullable<paths["/api/v1/bookings"]["get"]["parameters"]["query"]>;
export type ScheduleListParams =
  NonNullable<paths["/api/v1/schedules"]["get"]["parameters"]["query"]>;

export interface BookingFamilySummary {
  id: string;
  family_code: string;
  primary_contact_name: string;
  primary_contact_phone: string;
  primary_contact_email?: string | null;
  city?: string | null;
}

export interface BookingOpportunitySummary {
  id: string;
  opportunity_type: OpportunityType;
  current_stage: OpportunityStage;
  estimated_value: string;
}

export interface BookingUserSummary {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface Package {
  id: string;
  organization_id: string;
  branch_id: string;
  name: string;
  service_type: ServiceType;
  description?: string | null;
  price: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PackageAddon {
  id: string;
  organization_id: string;
  branch_id: string;
  name: string;
  description?: string | null;
  price: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookingItemAddon {
  id: string;
  booking_item_id: string;
  addon_id: string;
  price: string;
  created_at: string;
  addon?: PackageAddon | null;
}

export interface BookingItem {
  id: string;
  booking_id: string;
  package_id: string;
  service_type: ServiceType;
  price: string;
  discount: string;
  final_amount: string;
  status: string;
  created_at: string;
  updated_at: string;
  package?: Package | null;
  addons: BookingItemAddon[];
  schedules?: ShootSchedule[];
}

export interface Booking {
  id: string;
  organization_id: string;
  branch_id: string;
  family_id: string;
  opportunity_id: string;
  booking_number: string;
  booking_status: BookingStatus;
  total_amount: string;
  advance_received: string;
  balance_amount: string;
  booking_date: string;
  notes?: string | null;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  family?: BookingFamilySummary | null;
  opportunity?: BookingOpportunitySummary | null;
  items: BookingItem[];
}

export interface Assignment {
  id: string;
  shoot_schedule_id: string;
  user_id: string;
  role: AssignmentRole;
  assigned_at: string;
  user?: BookingUserSummary | null;
}

export interface ShootSchedule {
  id: string;
  booking_id: string;
  booking_item_id: string;
  scheduled_start: string;
  scheduled_end: string;
  location: string;
  shoot_status: ShootStatus;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  assignments: Assignment[];
  booking?: Booking | null;
}

export interface BookingMetrics {
  total_bookings: number;
  upcoming_shoots: number;
  completed_shoots: number;
  cancelled_shoots: number;
  revenue_booked: number;
  average_booking_value: number;
  photographer_utilization: number;
}
