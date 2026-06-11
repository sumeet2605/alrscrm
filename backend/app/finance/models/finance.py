from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.core.database import Base
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.bookings.models import Booking
    from app.families.models import Family
    from app.identity.models import Branch, Organization, User


class FinanceSettings(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "finance_settings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_finance_settings_branch_organization",
        ),
        UniqueConstraint("organization_id", "branch_id", name="uq_finance_settings_scope"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    registration_type: Mapped[str] = mapped_column(String(40), nullable=False)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    legal_name: Mapped[str] = mapped_column(String(180), nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    billing_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    billing_state: Mapped[str | None] = mapped_column(String(80), nullable=True)
    billing_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    default_due_days: Mapped[int] = mapped_column(nullable=False, default=15)
    invoice_prefix: Mapped[str] = mapped_column(String(20), nullable=False, default="INV")
    auto_create_booking_invoice: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    require_payment_before_delivery: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch | None] = sa_relationship(overlaps="organization")


class Invoice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "invoices"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_invoice_branch_organization",
        ),
        UniqueConstraint("invoice_number", name="uq_invoice_number"),
        CheckConstraint("subtotal >= 0", name="ck_invoice_subtotal_non_negative"),
        CheckConstraint("discount_amount >= 0", name="ck_invoice_discount_non_negative"),
        CheckConstraint("taxable_amount >= 0", name="ck_invoice_taxable_non_negative"),
        CheckConstraint("cgst_amount >= 0", name="ck_invoice_cgst_non_negative"),
        CheckConstraint("sgst_amount >= 0", name="ck_invoice_sgst_non_negative"),
        CheckConstraint("igst_amount >= 0", name="ck_invoice_igst_non_negative"),
        CheckConstraint("total_amount >= 0", name="ck_invoice_total_non_negative"),
        CheckConstraint("amount_paid >= 0", name="ck_invoice_paid_non_negative"),
        CheckConstraint("balance_due >= 0", name="ck_invoice_balance_non_negative"),
        CheckConstraint("amount_paid <= total_amount", name="ck_invoice_paid_lte_total"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(40), nullable=False)
    invoice_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    taxable_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    cgst_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    sgst_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    igst_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    seller_legal_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    seller_trade_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    seller_gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    seller_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    seller_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    buyer_billing_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    buyer_gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    buyer_billing_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    buyer_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    place_of_supply_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    supply_type: Mapped[str] = mapped_column(String(40), nullable=False)
    gst_registration_type: Mapped[str] = mapped_column(String(40), nullable=False)
    reverse_charge_applicable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    family: Mapped[Family] = sa_relationship()
    booking: Mapped[Booking] = sa_relationship()
    created_by_user: Mapped[User] = sa_relationship()
    line_items: Mapped[list[InvoiceLineItem]] = sa_relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )
    payments: Mapped[list[Payment]] = sa_relationship(back_populates="invoice")


class InvoiceLineItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "invoice_line_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_invoice_line_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_invoice_line_unit_non_negative"),
        CheckConstraint("discount_amount >= 0", name="ck_invoice_line_discount_non_negative"),
        CheckConstraint("taxable_amount >= 0", name="ck_invoice_line_taxable_non_negative"),
        CheckConstraint("tax_rate >= 0", name="ck_invoice_line_tax_rate_non_negative"),
        CheckConstraint("cgst_amount >= 0", name="ck_invoice_line_cgst_non_negative"),
        CheckConstraint("sgst_amount >= 0", name="ck_invoice_line_sgst_non_negative"),
        CheckConstraint("igst_amount >= 0", name="ck_invoice_line_igst_non_negative"),
        CheckConstraint("line_total >= 0", name="ck_invoice_line_total_non_negative"),
    )

    invoice_id: Mapped[UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    taxable_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    cgst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    cgst_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    sgst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    sgst_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    igst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    igst_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    service_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    sac_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    invoice: Mapped[Invoice] = sa_relationship(back_populates="line_items")


class Payment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_payment_branch_organization",
        ),
        UniqueConstraint("payment_number", name="uq_payment_number"),
        CheckConstraint("amount >= 0", name="ck_payment_amount_non_negative"),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    invoice_id: Mapped[UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False, index=True)
    payment_number: Mapped[str] = mapped_column(String(40), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    payment_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    transaction_reference: Mapped[str | None] = mapped_column(String(160), nullable=True)
    received_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    invoice: Mapped[Invoice] = sa_relationship(back_populates="payments")
    received_by_user: Mapped[User] = sa_relationship()
