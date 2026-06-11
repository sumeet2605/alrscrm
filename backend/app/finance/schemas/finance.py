from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.finance.enums import (
    GSTRegistrationType,
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
    SupplyType,
)


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_required(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Value is required")
    return cleaned


class FinanceSettingsUpdate(BaseModel):
    branch_id: UUID | None = None
    registration_type: GSTRegistrationType | None = None
    gstin: str | None = Field(default=None, max_length=15)
    legal_name: str | None = Field(default=None, min_length=1, max_length=180)
    trade_name: str | None = Field(default=None, max_length=180)
    billing_address: str | None = Field(default=None, max_length=4000)
    billing_state: str | None = Field(default=None, max_length=80)
    billing_state_code: str | None = Field(default=None, max_length=2)
    default_currency: str | None = Field(default=None, min_length=3, max_length=3)
    default_due_days: int | None = Field(default=None, ge=0, le=365)
    invoice_prefix: str | None = Field(default=None, min_length=1, max_length=20)
    auto_create_booking_invoice: bool | None = None
    require_payment_before_delivery: bool | None = None

    @field_validator(
        "gstin",
        "legal_name",
        "trade_name",
        "billing_address",
        "billing_state",
        "billing_state_code",
        "default_currency",
        "invoice_prefix",
    )
    @classmethod
    def clean_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class FinanceSettingsRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID | None = None
    registration_type: GSTRegistrationType
    gstin: str | None = None
    legal_name: str
    trade_name: str | None = None
    billing_address: str | None = None
    billing_state: str | None = None
    billing_state_code: str | None = None
    default_currency: str
    default_due_days: int
    invoice_prefix: str
    auto_create_booking_invoice: bool
    require_payment_before_delivery: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceLineItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, max_digits=5, decimal_places=2)
    cgst_rate: Decimal = Field(default=Decimal("0"), ge=0, max_digits=5, decimal_places=2)
    cgst_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    sgst_rate: Decimal = Field(default=Decimal("0"), ge=0, max_digits=5, decimal_places=2)
    sgst_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    igst_rate: Decimal = Field(default=Decimal("0"), ge=0, max_digits=5, decimal_places=2)
    igst_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    service_type: str = Field(min_length=1, max_length=40)
    sac_code: str | None = Field(default=None, max_length=20)

    @field_validator("description", "service_type")
    @classmethod
    def clean_required_strings(cls, value: str) -> str:
        return _clean_required(value)

    @field_validator("sac_code")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class InvoiceBase(BaseModel):
    organization_id: UUID
    branch_id: UUID
    family_id: UUID
    booking_id: UUID
    due_date: date
    currency: str = Field(default="INR", min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=5000)
    seller_legal_name: str | None = Field(default=None, max_length=180)
    seller_trade_name: str | None = Field(default=None, max_length=180)
    seller_gstin: str | None = Field(default=None, max_length=15)
    seller_address: str | None = Field(default=None, max_length=4000)
    seller_state_code: str | None = Field(default=None, max_length=2)
    buyer_billing_name: str | None = Field(default=None, max_length=180)
    buyer_gstin: str | None = Field(default=None, max_length=15)
    buyer_billing_address: str | None = Field(default=None, max_length=4000)
    buyer_state_code: str | None = Field(default=None, max_length=2)
    place_of_supply_state_code: str | None = Field(default=None, max_length=2)
    supply_type: SupplyType = SupplyType.NON_GST
    gst_registration_type: GSTRegistrationType = GSTRegistrationType.UNREGISTERED
    reverse_charge_applicable: bool = False
    line_items: list[InvoiceLineItemCreate] = Field(min_length=1)

    @field_validator(
        "currency",
        "notes",
        "seller_legal_name",
        "seller_trade_name",
        "seller_gstin",
        "seller_address",
        "seller_state_code",
        "buyer_billing_name",
        "buyer_gstin",
        "buyer_billing_address",
        "buyer_state_code",
        "place_of_supply_state_code",
    )
    @classmethod
    def clean_optional_invoice_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    due_date: date | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=5000)
    seller_legal_name: str | None = Field(default=None, max_length=180)
    seller_trade_name: str | None = Field(default=None, max_length=180)
    seller_gstin: str | None = Field(default=None, max_length=15)
    seller_address: str | None = Field(default=None, max_length=4000)
    seller_state_code: str | None = Field(default=None, max_length=2)
    buyer_billing_name: str | None = Field(default=None, max_length=180)
    buyer_gstin: str | None = Field(default=None, max_length=15)
    buyer_billing_address: str | None = Field(default=None, max_length=4000)
    buyer_state_code: str | None = Field(default=None, max_length=2)
    place_of_supply_state_code: str | None = Field(default=None, max_length=2)
    supply_type: SupplyType | None = None
    gst_registration_type: GSTRegistrationType | None = None
    reverse_charge_applicable: bool | None = None
    line_items: list[InvoiceLineItemCreate] | None = None

    @field_validator(
        "currency",
        "notes",
        "seller_legal_name",
        "seller_trade_name",
        "seller_gstin",
        "seller_address",
        "seller_state_code",
        "buyer_billing_name",
        "buyer_gstin",
        "buyer_billing_address",
        "buyer_state_code",
        "place_of_supply_state_code",
    )
    @classmethod
    def clean_optional_invoice_update_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class InvoiceLineItemRead(BaseModel):
    id: UUID
    invoice_id: UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    tax_rate: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    line_total: Decimal
    service_type: str
    sac_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InvoicePaymentRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    invoice_id: UUID
    payment_number: str
    amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_reference: str | None = None
    received_date: date
    notes: str | None = None
    received_by_user_id: UUID
    created_at: datetime
    refunded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    family_id: UUID
    booking_id: UUID
    invoice_number: str
    invoice_status: InvoiceStatus
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    currency: str
    issue_date: date | None = None
    due_date: date
    notes: str | None = None
    created_by_user_id: UUID
    seller_legal_name: str | None = None
    seller_trade_name: str | None = None
    seller_gstin: str | None = None
    seller_address: str | None = None
    seller_state_code: str | None = None
    buyer_billing_name: str | None = None
    buyer_gstin: str | None = None
    buyer_billing_address: str | None = None
    buyer_state_code: str | None = None
    place_of_supply_state_code: str | None = None
    supply_type: SupplyType
    gst_registration_type: GSTRegistrationType
    reverse_charge_applicable: bool
    voided_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    line_items: list[InvoiceLineItemRead] = Field(default_factory=list)
    payments: list[InvoicePaymentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: PaymentMethod
    payment_status: PaymentStatus = PaymentStatus.COMPLETED
    transaction_reference: str | None = Field(default=None, max_length=160)
    received_date: date = Field(default_factory=date.today)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("transaction_reference", "notes")
    @classmethod
    def clean_payment_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class PaymentRead(BaseModel):
    id: UUID
    organization_id: UUID
    branch_id: UUID
    invoice_id: UUID
    payment_number: str
    amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_reference: str | None = None
    received_date: date
    notes: str | None = None
    received_by_user_id: UUID
    created_at: datetime
    refunded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class FinanceMetricsRead(BaseModel):
    revenue_this_month: Decimal
    revenue_this_year: Decimal
    outstanding_amount: Decimal
    paid_amount: Decimal
    overdue_amount: Decimal
    invoices_by_status: dict[str, int]
    payments_by_method: dict[str, int]
