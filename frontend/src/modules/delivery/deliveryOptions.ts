import type { DeliveryStatus, ZipGenerationStatus } from "../../types/delivery";

export const deliveryStatuses: DeliveryStatus[] = [
  "PENDING",
  "ZIP_GENERATING",
  "READY",
  "SENT",
  "DELIVERED",
  "EXPIRED",
  "REOPEN_REQUESTED",
  "REOPENED",
  "CLOSED"
];

export const zipGenerationStatuses: ZipGenerationStatus[] = [
  "PENDING",
  "GENERATING",
  "COMPLETED",
  "FAILED"
];

export function labelFromEnum(value?: string | null): string {
  if (!value) return "-";
  return value
    .split("_")
    .map((part) => part.charAt(0) + part.slice(1).toLowerCase())
    .join(" ");
}

export function deliveryStatusColor(status: DeliveryStatus): string {
  const colors: Record<DeliveryStatus, string> = {
    PENDING: "default",
    ZIP_GENERATING: "processing",
    READY: "blue",
    SENT: "purple",
    DELIVERED: "green",
    EXPIRED: "red",
    REOPEN_REQUESTED: "orange",
    REOPENED: "gold",
    CLOSED: "default"
  };
  return colors[status];
}

export function zipStatusColor(status: ZipGenerationStatus): string {
  const colors: Record<ZipGenerationStatus, string> = {
    PENDING: "default",
    GENERATING: "processing",
    COMPLETED: "green",
    FAILED: "red"
  };
  return colors[status];
}
