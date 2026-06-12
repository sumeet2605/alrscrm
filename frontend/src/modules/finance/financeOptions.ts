import type { InvoiceStatus, PaymentMethod, PaymentStatus } from "../../types/finance";

export const invoiceStatuses: InvoiceStatus[] = [
  "DRAFT",
  "ISSUED",
  "PARTIALLY_PAID",
  "PAID",
  "VOID",
  "OVERDUE"
];

export const paymentMethods: PaymentMethod[] = [
  "CASH",
  "UPI",
  "BANK_TRANSFER",
  "CARD",
  "CHEQUE",
  "OTHER"
];

export const paymentStatuses: PaymentStatus[] = ["PENDING", "COMPLETED", "FAILED", "REFUNDED"];

export function labelFromEnum(value?: string | null): string {
  if (!value) return "-";
  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function invoiceStatusColor(status: InvoiceStatus): string {
  const colors: Record<InvoiceStatus, string> = {
    DRAFT: "default",
    ISSUED: "processing",
    PARTIALLY_PAID: "warning",
    PAID: "success",
    VOID: "error",
    OVERDUE: "volcano"
  };
  return colors[status];
}

export function paymentStatusColor(status: PaymentStatus): string {
  const colors: Record<PaymentStatus, string> = {
    PENDING: "warning",
    COMPLETED: "success",
    FAILED: "error",
    REFUNDED: "default"
  };
  return colors[status];
}

export function canManageFinance(roleNames: string[]): boolean {
  return roleNames.some((role) =>
    ["Super Admin", "Organization Admin", "Owner", "Branch Manager"].includes(role)
  );
}

export function money(value?: string | number | null): string {
  return `₹${Number(value ?? 0).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2
  })}`;
}
