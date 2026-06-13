import { apiClient } from "./http";
import type { ApiEnvelope } from "../types/api";
import type {
  FinanceListResult,
  FinanceMetrics,
  FinanceSettings,
  Invoice,
  InvoiceListParams,
  InvoicePayload,
  InvoiceUpdatePayload,
  Payment,
  PaymentListParams,
  PaymentPayload
} from "../types/finance";

export async function getFinanceSettings(branchId?: string): Promise<FinanceSettings> {
  const response = await apiClient.get<ApiEnvelope<FinanceSettings>>("/finance/settings", {
    params: branchId ? { branch_id: branchId } : undefined
  });
  return response.data.data;
}

export async function getFinanceMetrics(): Promise<FinanceMetrics> {
  const response = await apiClient.get<ApiEnvelope<FinanceMetrics>>("/finance/metrics");
  return response.data.data;
}

export async function listInvoices(
  params: InvoiceListParams
): Promise<FinanceListResult<Invoice>> {
  const response = await apiClient.get<ApiEnvelope<Invoice[]>>("/invoices", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createInvoice(payload: InvoicePayload): Promise<Invoice> {
  const response = await apiClient.post<ApiEnvelope<Invoice>>("/invoices", payload);
  return response.data.data;
}

export async function getInvoice(id: string): Promise<Invoice> {
  const response = await apiClient.get<ApiEnvelope<Invoice>>(`/invoices/${id}`);
  return response.data.data;
}

export async function downloadInvoicePdf(id: string): Promise<Blob> {
  const response = await apiClient.get<Blob>(`/invoices/${id}/pdf`, { responseType: "blob" });
  return response.data;
}

export async function updateInvoice(id: string, payload: InvoiceUpdatePayload): Promise<Invoice> {
  const response = await apiClient.put<ApiEnvelope<Invoice>>(`/invoices/${id}`, payload);
  return response.data.data;
}

export async function issueInvoice(id: string): Promise<Invoice> {
  const response = await apiClient.post<ApiEnvelope<Invoice>>(`/invoices/${id}/issue`);
  return response.data.data;
}

export async function voidInvoice(id: string): Promise<Invoice> {
  const response = await apiClient.post<ApiEnvelope<Invoice>>(`/invoices/${id}/void`);
  return response.data.data;
}

export async function listPayments(
  params: PaymentListParams
): Promise<FinanceListResult<Payment>> {
  const response = await apiClient.get<ApiEnvelope<Payment[]>>("/payments", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function createPayment(payload: PaymentPayload): Promise<Payment> {
  const response = await apiClient.post<ApiEnvelope<Payment>>("/payments", payload);
  return response.data.data;
}

export async function getPayment(id: string): Promise<Payment> {
  const response = await apiClient.get<ApiEnvelope<Payment>>(`/payments/${id}`);
  return response.data.data;
}

export async function downloadPaymentReceipt(id: string): Promise<Blob> {
  const response = await apiClient.get<Blob>(`/payments/${id}/receipt`, {
    responseType: "blob"
  });
  return response.data;
}
