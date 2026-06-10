import { apiClient } from "./http";
import type { ApiEnvelope, PaginationMeta } from "../types/api";
import type {
  AddonPayload,
  AddonUpdatePayload,
  Assignment,
  AssignmentPayload,
  Booking,
  BookingListParams,
  BookingMetrics,
  BookingPayload,
  BookingUpdatePayload,
  Package,
  PackageAddon,
  PackagePayload,
  PackageUpdatePayload,
  ScheduleListParams,
  SchedulePayload,
  ScheduleUpdatePayload,
  ShootSchedule
} from "../types/bookings";

export interface ListResult<T> {
  items: T[];
  meta: PaginationMeta;
}

export async function listBookings(params: BookingListParams): Promise<ListResult<Booking>> {
  const response = await apiClient.get<ApiEnvelope<Booking[]>>("/bookings", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function getBooking(id: string): Promise<Booking> {
  const response = await apiClient.get<ApiEnvelope<Booking>>(`/bookings/${id}`);
  return response.data.data;
}

export async function createBooking(payload: BookingPayload): Promise<Booking> {
  const response = await apiClient.post<ApiEnvelope<Booking>>("/bookings", payload);
  return response.data.data;
}

export async function updateBooking(id: string, payload: BookingUpdatePayload): Promise<Booking> {
  const response = await apiClient.put<ApiEnvelope<Booking>>(`/bookings/${id}`, payload);
  return response.data.data;
}

export async function deleteBooking(id: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(`/bookings/${id}`);
}

export async function getBookingMetrics(): Promise<BookingMetrics> {
  const response = await apiClient.get<ApiEnvelope<BookingMetrics>>("/bookings/metrics");
  return response.data.data;
}

export async function listPackages(): Promise<Package[]> {
  const response = await apiClient.get<ApiEnvelope<Package[]>>("/packages");
  return response.data.data;
}

export async function createPackage(payload: PackagePayload): Promise<Package> {
  const response = await apiClient.post<ApiEnvelope<Package>>("/packages", payload);
  return response.data.data;
}

export async function updatePackage(id: string, payload: PackageUpdatePayload): Promise<Package> {
  const response = await apiClient.put<ApiEnvelope<Package>>(`/packages/${id}`, payload);
  return response.data.data;
}

export async function listAddons(): Promise<PackageAddon[]> {
  const response = await apiClient.get<ApiEnvelope<PackageAddon[]>>("/addons");
  return response.data.data;
}

export async function createAddon(payload: AddonPayload): Promise<PackageAddon> {
  const response = await apiClient.post<ApiEnvelope<PackageAddon>>("/addons", payload);
  return response.data.data;
}

export async function updateAddon(id: string, payload: AddonUpdatePayload): Promise<PackageAddon> {
  const response = await apiClient.put<ApiEnvelope<PackageAddon>>(`/addons/${id}`, payload);
  return response.data.data;
}

export async function listSchedules(
  params: ScheduleListParams
): Promise<ListResult<ShootSchedule>> {
  const response = await apiClient.get<ApiEnvelope<ShootSchedule[]>>("/schedules", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createSchedule(payload: SchedulePayload): Promise<ShootSchedule> {
  const response = await apiClient.post<ApiEnvelope<ShootSchedule>>("/schedules", payload);
  return response.data.data;
}

export async function updateSchedule(
  id: string,
  payload: ScheduleUpdatePayload
): Promise<ShootSchedule> {
  const response = await apiClient.put<ApiEnvelope<ShootSchedule>>(`/schedules/${id}`, payload);
  return response.data.data;
}

export async function listAssignments(photographerId?: string): Promise<Assignment[]> {
  const response = await apiClient.get<ApiEnvelope<Assignment[]>>("/assignments", {
    params: photographerId ? { photographer_id: photographerId } : undefined
  });
  return response.data.data;
}

export async function createAssignment(payload: AssignmentPayload): Promise<Assignment> {
  const response = await apiClient.post<ApiEnvelope<Assignment>>("/assignments", payload);
  return response.data.data;
}

export async function deleteAssignment(id: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(`/assignments/${id}`);
}
