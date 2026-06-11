import type { PaginationMeta } from "./api";

export type GSTRegistrationType = "REGULAR" | "COMPOSITION" | "EXEMPT" | "UNREGISTERED";
export type SupplyType = "INTRA_STATE" | "INTER_STATE" | "NON_GST";
export type InvoiceStatus = "DRAFT" | "ISSUED" | "PARTIALLY_PAID" | "PAID" | "VOID" | "OVERDUE";
export type PaymentMethod = "CASH" | "UPI" | "BANK_TRANSFER" | "CARD" | "CHEQUE" | "OTHER";
export type PaymentStatus = "PENDING" | "COMPLETED" | "FAILED" | "REFUNDED";

export interface FinanceListResult<T> {
  items: T[];
  meta: PaginationMeta;
}

export interface FinanceSettings {
  id: string;
  organization_id: string;
  branch_id?: string | null;
  registration_type: GSTRegistrationType;
  gstin?: string | null;
  legal_name: string;
  trade_name?: string | null;
  billing_address?: string | null;
  billing_state_code?: string | null;
  billing_email?: string | null;
  billing_phone?: string | null;
  default_currency: string;
  default_due_days: number;
  invoice_prefix: string;
  auto_create_booking_invoice: boolean;
  require_payment_before_delivery: boolean;
  created_at: string;
  updated_at: string;
}

export interface InvoiceLineItemPayload {
  description: string;
  quantity: string;
  unit_price: string;
  discount_amount?: string;
  tax_rate?: string;
  cgst_rate?: string;
  cgst_amount?: string;
  sgst_rate?: string;
  sgst_amount?: string;
  igst_rate?: string;
  igst_amount?: string;
  service_type?: string | null;
  sac_code?: string | null;
}

export interface InvoicePayload {
  organization_id: string;
  branch_id: string;
  family_id: string;
  booking_id: string;
  currency?: string;
  due_date?: string | null;
  notes?: string | null;
  seller_legal_name?: string | null;
  seller_trade_name?: string | null;
  seller_gstin?: string | null;
  seller_address?: string | null;
  seller_state_code?: string | null;
  buyer_billing_name: string;
  buyer_gstin?: string | null;
  buyer_billing_address?: string | null;
  buyer_state_code?: string | null;
  place_of_supply_state_code?: string | null;
  supply_type: SupplyType;
  gst_registration_type: GSTRegistrationType;
  reverse_charge_applicable?: boolean;
  line_items: InvoiceLineItemPayload[];
}

export interface InvoiceUpdatePayload extends Partial<Omit<InvoicePayload, "line_items">> {
  line_items?: InvoiceLineItemPayload[];
}

export interface InvoiceLineItem {
  id: string;
  invoice_id: string;
  description: string;
  quantity: string;
  unit_price: string;
  discount_amount: string;
  taxable_amount: string;
  tax_rate: string;
  cgst_rate: string;
  cgst_amount: string;
  sgst_rate: string;
  sgst_amount: string;
  igst_rate: string;
  igst_amount: string;
  line_total: string;
  service_type?: string | null;
  sac_code?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: string;
  organization_id: string;
  branch_id: string;
  family_id: string;
  booking_id: string;
  invoice_number: string;
  invoice_status: InvoiceStatus;
  subtotal: string;
  discount_amount: string;
  taxable_amount: string;
  cgst_amount: string;
  sgst_amount: string;
  igst_amount: string;
  total_amount: string;
  amount_paid: string;
  balance_due: string;
  currency: string;
  issue_date: string;
  due_date?: string | null;
  notes?: string | null;
  seller_legal_name?: string | null;
  seller_trade_name?: string | null;
  seller_gstin?: string | null;
  seller_address?: string | null;
  seller_state_code?: string | null;
  buyer_billing_name: string;
  buyer_gstin?: string | null;
  buyer_billing_address?: string | null;
  buyer_state_code?: string | null;
  place_of_supply_state_code?: string | null;
  supply_type: SupplyType;
  gst_registration_type: GSTRegistrationType;
  reverse_charge_applicable: boolean;
  created_by_user_id?: string | null;
  voided_at?: string | null;
  created_at: string;
  updated_at: string;
  line_items: InvoiceLineItem[];
  payments: Payment[];
}

export interface InvoiceListParams {
  page?: number;
  page_size?: number;
  branch_id?: string;
  invoice_status?: InvoiceStatus;
  booking_id?: string;
  family_id?: string;
}

export interface PaymentPayload {
  invoice_id: string;
  amount: string;
  payment_method: PaymentMethod;
  payment_status?: PaymentStatus;
  transaction_reference?: string | null;
  received_date?: string | null;
  notes?: string | null;
}

export interface Payment {
  id: string;
  organization_id: string;
  branch_id: string;
  invoice_id: string;
  payment_number: string;
  amount: string;
  payment_method: PaymentMethod;
  payment_status: PaymentStatus;
  transaction_reference?: string | null;
  received_date: string;
  notes?: string | null;
  received_by_user_id?: string | null;
  refunded_at?: string | null;
  created_at: string;
}

export interface PaymentListParams {
  page?: number;
  page_size?: number;
  branch_id?: string;
  payment_status?: PaymentStatus;
  payment_method?: PaymentMethod;
  invoice_id?: string;
}

export interface FinanceMetrics {
  revenue_this_month: string;
  revenue_this_year: string;
  outstanding_amount: string;
  paid_amount: string;
  overdue_amount: string;
  invoices_by_status: Record<string, number>;
  payments_by_method: Record<string, number>;
}
