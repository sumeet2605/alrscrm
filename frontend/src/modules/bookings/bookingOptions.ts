import type { AssignmentRole, BookingStatus, ServiceType, ShootStatus } from "../../types/bookings";

export const serviceTypes: ServiceType[] = ["MATERNITY", "NEWBORN", "FAMILY", "MILESTONE", "CAKE_SMASH"];
export const bookingStatuses: BookingStatus[] = [
  "PENDING_ADVANCE",
  "CONFIRMED",
  "SCHEDULED",
  "COMPLETED",
  "CANCELLED"
];
export const shootStatuses: ShootStatus[] = [
  "NOT_SCHEDULED",
  "SCHEDULED",
  "IN_PROGRESS",
  "COMPLETED",
  "RESCHEDULED",
  "CANCELLED"
];
export const assignmentRoles: AssignmentRole[] = [
  "LEAD_PHOTOGRAPHER",
  "SECOND_PHOTOGRAPHER",
  "ASSISTANT"
];

export function labelFromEnum(value: string): string {
  return value
    .split("_")
    .map((part) => `${part.slice(0, 1)}${part.slice(1).toLowerCase()}`)
    .join(" ");
}

export function canManageBookings(roleNames: string[]): boolean {
  return roleNames.some((role) =>
    ["Super Admin", "Owner", "Branch Manager", "Sales Executive"].includes(role)
  );
}

export function canAssignPhotographers(roleNames: string[]): boolean {
  return roleNames.some((role) => ["Super Admin", "Owner", "Branch Manager"].includes(role));
}

export function canManagePackages(roleNames: string[]): boolean {
  return roleNames.some((role) => ["Super Admin", "Owner", "Branch Manager"].includes(role));
}
