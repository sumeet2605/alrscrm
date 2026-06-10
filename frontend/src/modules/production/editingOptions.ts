import type { EditingPriority, EditingStatus } from "../../types/editing";

export const editingStatuses: EditingStatus[] = [
  "PENDING",
  "ASSIGNED",
  "IN_PROGRESS",
  "READY_FOR_REVIEW",
  "APPROVED",
  "REJECTED",
  "READY_FOR_DELIVERY"
];

export const editingPriorities: EditingPriority[] = ["LOW", "NORMAL", "HIGH", "URGENT"];

export function labelFromEnum(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0) + part.slice(1).toLowerCase())
    .join(" ");
}

export function editingStatusColor(status: EditingStatus): string {
  const colors: Record<EditingStatus, string> = {
    PENDING: "default",
    ASSIGNED: "blue",
    IN_PROGRESS: "processing",
    READY_FOR_REVIEW: "gold",
    APPROVED: "green",
    REJECTED: "red",
    READY_FOR_DELIVERY: "purple"
  };
  return colors[status];
}

export function priorityColor(priority: EditingPriority): string {
  const colors: Record<EditingPriority, string> = {
    LOW: "default",
    NORMAL: "blue",
    HIGH: "orange",
    URGENT: "red"
  };
  return colors[priority];
}
