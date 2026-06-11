"""create finance mvp

Revision ID: 202606100017
Revises: 202606100016
Create Date: 2026-06-11 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606100017"
down_revision: str | None = "202606100016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS invoice_number_seq START WITH 1 INCREMENT BY 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS payment_number_seq START WITH 1 INCREMENT BY 1")

    op.create_table(
        "finance_settings",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=True),
        sa.Column("registration_type", sa.String(length=40), nullable=False),
        sa.Column("gstin", sa.String(length=15), nullable=True),
        sa.Column("legal_name", sa.String(length=180), nullable=False),
        sa.Column("trade_name", sa.String(length=180), nullable=True),
        sa.Column("billing_address", sa.Text(), nullable=True),
        sa.Column("billing_state", sa.String(length=80), nullable=True),
        sa.Column("billing_state_code", sa.String(length=2), nullable=True),
        sa.Column("default_currency", sa.String(length=3), nullable=False),
        sa.Column("default_due_days", sa.Integer(), nullable=False),
        sa.Column("invoice_prefix", sa.String(length=20), nullable=False),
        sa.Column("auto_create_booking_invoice", sa.Boolean(), nullable=False),
        sa.Column("require_payment_before_delivery", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_finance_settings_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "branch_id", name="uq_finance_settings_scope"),
    )
    op.create_index(op.f("ix_finance_settings_branch_id"), "finance_settings", ["branch_id"])

    op.create_table(
        "invoices",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("invoice_number", sa.String(length=40), nullable=False),
        sa.Column("invoice_status", sa.String(length=40), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("taxable_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("cgst_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("sgst_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("igst_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("amount_paid", sa.Numeric(12, 2), nullable=False),
        sa.Column("balance_due", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("seller_legal_name", sa.String(length=180), nullable=True),
        sa.Column("seller_trade_name", sa.String(length=180), nullable=True),
        sa.Column("seller_gstin", sa.String(length=15), nullable=True),
        sa.Column("seller_address", sa.Text(), nullable=True),
        sa.Column("seller_state_code", sa.String(length=2), nullable=True),
        sa.Column("buyer_billing_name", sa.String(length=180), nullable=True),
        sa.Column("buyer_gstin", sa.String(length=15), nullable=True),
        sa.Column("buyer_billing_address", sa.Text(), nullable=True),
        sa.Column("buyer_state_code", sa.String(length=2), nullable=True),
        sa.Column("place_of_supply_state_code", sa.String(length=2), nullable=True),
        sa.Column("supply_type", sa.String(length=40), nullable=False),
        sa.Column("gst_registration_type", sa.String(length=40), nullable=False),
        sa.Column("reverse_charge_applicable", sa.Boolean(), nullable=False),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("amount_paid <= total_amount", name="ck_invoice_paid_lte_total"),
        sa.CheckConstraint("amount_paid >= 0", name="ck_invoice_paid_non_negative"),
        sa.CheckConstraint("balance_due >= 0", name="ck_invoice_balance_non_negative"),
        sa.CheckConstraint("cgst_amount >= 0", name="ck_invoice_cgst_non_negative"),
        sa.CheckConstraint("discount_amount >= 0", name="ck_invoice_discount_non_negative"),
        sa.CheckConstraint("igst_amount >= 0", name="ck_invoice_igst_non_negative"),
        sa.CheckConstraint("sgst_amount >= 0", name="ck_invoice_sgst_non_negative"),
        sa.CheckConstraint("subtotal >= 0", name="ck_invoice_subtotal_non_negative"),
        sa.CheckConstraint("taxable_amount >= 0", name="ck_invoice_taxable_non_negative"),
        sa.CheckConstraint("total_amount >= 0", name="ck_invoice_total_non_negative"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_invoice_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number", name="uq_invoice_number"),
    )
    op.create_index(op.f("ix_invoices_booking_id"), "invoices", ["booking_id"])
    op.create_index(op.f("ix_invoices_branch_id"), "invoices", ["branch_id"])
    op.create_index(op.f("ix_invoices_due_date"), "invoices", ["due_date"])
    op.create_index(op.f("ix_invoices_family_id"), "invoices", ["family_id"])
    op.create_index(op.f("ix_invoices_invoice_status"), "invoices", ["invoice_status"])
    op.create_index(op.f("ix_invoices_issue_date"), "invoices", ["issue_date"])

    op.create_table(
        "invoice_line_items",
        sa.Column("invoice_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("taxable_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("cgst_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("cgst_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("sgst_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("sgst_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("igst_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("igst_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("service_type", sa.String(length=40), nullable=False),
        sa.Column("sac_code", sa.String(length=20), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("cgst_amount >= 0", name="ck_invoice_line_cgst_non_negative"),
        sa.CheckConstraint("discount_amount >= 0", name="ck_invoice_line_discount_non_negative"),
        sa.CheckConstraint("igst_amount >= 0", name="ck_invoice_line_igst_non_negative"),
        sa.CheckConstraint("line_total >= 0", name="ck_invoice_line_total_non_negative"),
        sa.CheckConstraint("quantity > 0", name="ck_invoice_line_quantity_positive"),
        sa.CheckConstraint("sgst_amount >= 0", name="ck_invoice_line_sgst_non_negative"),
        sa.CheckConstraint("tax_rate >= 0", name="ck_invoice_line_tax_rate_non_negative"),
        sa.CheckConstraint("taxable_amount >= 0", name="ck_invoice_line_taxable_non_negative"),
        sa.CheckConstraint("unit_price >= 0", name="ck_invoice_line_unit_non_negative"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoice_line_items_invoice_id"), "invoice_line_items", ["invoice_id"])
    op.create_index(
        op.f("ix_invoice_line_items_service_type"),
        "invoice_line_items",
        ["service_type"],
    )

    op.create_table(
        "payments",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("invoice_id", sa.Uuid(), nullable=False),
        sa.Column("payment_number", sa.String(length=40), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=40), nullable=False),
        sa.Column("payment_status", sa.String(length=40), nullable=False),
        sa.Column("transaction_reference", sa.String(length=160), nullable=True),
        sa.Column("received_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("received_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("amount >= 0", name="ck_payment_amount_non_negative"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["received_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_payment_branch_organization",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_number", name="uq_payment_number"),
    )
    op.create_index(op.f("ix_payments_branch_id"), "payments", ["branch_id"])
    op.create_index(op.f("ix_payments_invoice_id"), "payments", ["invoice_id"])
    op.create_index(op.f("ix_payments_payment_method"), "payments", ["payment_method"])
    op.create_index(op.f("ix_payments_payment_status"), "payments", ["payment_status"])
    op.create_index(op.f("ix_payments_received_date"), "payments", ["received_date"])


def downgrade() -> None:
    op.drop_index(op.f("ix_payments_received_date"), table_name="payments")
    op.drop_index(op.f("ix_payments_payment_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_payment_method"), table_name="payments")
    op.drop_index(op.f("ix_payments_invoice_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_branch_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(op.f("ix_invoice_line_items_service_type"), table_name="invoice_line_items")
    op.drop_index(op.f("ix_invoice_line_items_invoice_id"), table_name="invoice_line_items")
    op.drop_table("invoice_line_items")
    op.drop_index(op.f("ix_invoices_issue_date"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_invoice_status"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_family_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_due_date"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_branch_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_booking_id"), table_name="invoices")
    op.drop_table("invoices")
    op.drop_index(op.f("ix_finance_settings_branch_id"), table_name="finance_settings")
    op.drop_table("finance_settings")
    op.execute("DROP SEQUENCE IF EXISTS payment_number_seq")
    op.execute("DROP SEQUENCE IF EXISTS invoice_number_seq")
