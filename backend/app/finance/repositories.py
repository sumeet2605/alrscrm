from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, text
from sqlalchemy.orm import Session, selectinload

from app.finance.enums import InvoiceStatus, PaymentStatus
from app.finance.models import FinanceSettings, Invoice, InvoiceLineItem, Payment
from app.shared.pagination import PageResult, paginate_query


class FinanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def invoice_options(self):
        return (selectinload(Invoice.line_items), selectinload(Invoice.payments))

    def get_settings(self, organization_id: UUID, branch_id: UUID | None) -> FinanceSettings | None:
        return (
            self.db.query(FinanceSettings)
            .filter(
                FinanceSettings.organization_id == organization_id,
                FinanceSettings.branch_id == branch_id,
            )
            .one_or_none()
        )

    def add_settings(self, settings: FinanceSettings) -> FinanceSettings:
        self.db.add(settings)
        return settings

    def next_invoice_number(self, prefix: str = "INV") -> str:
        year = datetime.now(UTC).year
        if self.db.bind and self.db.bind.dialect.name == "postgresql":
            sequence_value = self.db.execute(
                text("SELECT nextval('invoice_number_seq')")
            ).scalar_one()
            return f"{prefix}-{year}-{int(sequence_value):06d}"
        count = self.db.query(Invoice).count() + 1
        return f"{prefix}-{year}-{count:06d}"

    def next_payment_number(self) -> str:
        year = datetime.now(UTC).year
        if self.db.bind and self.db.bind.dialect.name == "postgresql":
            sequence_value = self.db.execute(
                text("SELECT nextval('payment_number_seq')")
            ).scalar_one()
            return f"PAY-{year}-{int(sequence_value):06d}"
        count = self.db.query(Payment).count() + 1
        return f"PAY-{year}-{count:06d}"

    def add_invoice(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        return invoice

    def get_invoice(self, invoice_id: UUID) -> Invoice | None:
        return (
            self.db.query(Invoice)
            .options(*self.invoice_options())
            .filter(Invoice.id == invoice_id)
            .one_or_none()
        )

    def get_invoice_for_update(self, invoice_id: UUID) -> Invoice | None:
        query = self.db.query(Invoice).filter(Invoice.id == invoice_id)
        if self.db.bind and self.db.bind.dialect.name != "sqlite":
            query = query.with_for_update()
        return query.one_or_none()

    def list_invoices(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None,
        branch_id: UUID | None,
        invoice_status: str | None = None,
        booking_id: UUID | None = None,
        family_id: UUID | None = None,
    ) -> PageResult:
        query = self.db.query(Invoice).options(*self.invoice_options())
        query = self._apply_invoice_scope(query, organization_id, branch_id)
        if invoice_status is not None:
            query = query.filter(Invoice.invoice_status == invoice_status)
        if booking_id is not None:
            query = query.filter(Invoice.booking_id == booking_id)
        if family_id is not None:
            query = query.filter(Invoice.family_id == family_id)
        return paginate_query(
            query.order_by(Invoice.created_at.desc(), Invoice.invoice_number.desc()),
            page,
            page_size,
        )

    def replace_line_items(self, invoice: Invoice, line_items: list[InvoiceLineItem]) -> None:
        invoice.line_items.clear()
        invoice.line_items.extend(line_items)

    def add_payment(self, payment: Payment) -> Payment:
        self.db.add(payment)
        return payment

    def get_payment(self, payment_id: UUID) -> Payment | None:
        return self.db.get(Payment, payment_id)

    def list_payments(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None,
        branch_id: UUID | None,
        payment_status: str | None = None,
        payment_method: str | None = None,
        invoice_id: UUID | None = None,
    ) -> PageResult:
        query = self.db.query(Payment)
        query = self._apply_payment_scope(query, organization_id, branch_id)
        if payment_status is not None:
            query = query.filter(Payment.payment_status == payment_status)
        if payment_method is not None:
            query = query.filter(Payment.payment_method == payment_method)
        if invoice_id is not None:
            query = query.filter(Payment.invoice_id == invoice_id)
        return paginate_query(query.order_by(Payment.created_at.desc()), page, page_size)

    def metrics(self, organization_id: UUID | None, branch_id: UUID | None) -> dict:
        today = date.today()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        invoice_query = self._apply_invoice_scope(
            self.db.query(Invoice), organization_id, branch_id
        )
        payment_query = self._apply_payment_scope(
            self.db.query(Payment), organization_id, branch_id
        )
        completed_payments = payment_query.filter(
            Payment.payment_status == PaymentStatus.COMPLETED.value
        )
        revenue_this_month = completed_payments.filter(
            Payment.received_date >= month_start
        ).with_entities(func.coalesce(func.sum(Payment.amount), 0)).scalar() or Decimal("0")
        revenue_this_year = completed_payments.filter(
            Payment.received_date >= year_start
        ).with_entities(func.coalesce(func.sum(Payment.amount), 0)).scalar() or Decimal("0")
        paid_amount = completed_payments.with_entities(
            func.coalesce(func.sum(Payment.amount), 0)
        ).scalar() or Decimal("0")
        open_invoice_query = invoice_query.filter(
            Invoice.invoice_status != InvoiceStatus.VOID.value
        )
        outstanding_amount = open_invoice_query.with_entities(
            func.coalesce(func.sum(Invoice.balance_due), 0)
        ).scalar() or Decimal("0")
        overdue_amount = open_invoice_query.filter(
            Invoice.due_date < today, Invoice.balance_due > 0
        ).with_entities(func.coalesce(func.sum(Invoice.balance_due), 0)).scalar() or Decimal("0")
        status_rows = (
            invoice_query.with_entities(Invoice.invoice_status, func.count(Invoice.id))
            .group_by(Invoice.invoice_status)
            .all()
        )
        method_rows = (
            payment_query.with_entities(Payment.payment_method, func.count(Payment.id))
            .group_by(Payment.payment_method)
            .all()
        )
        return {
            "revenue_this_month": revenue_this_month,
            "revenue_this_year": revenue_this_year,
            "outstanding_amount": outstanding_amount,
            "paid_amount": paid_amount,
            "overdue_amount": overdue_amount,
            "invoices_by_status": {status: count for status, count in status_rows},
            "payments_by_method": {method: count for method, count in method_rows},
        }

    def _apply_invoice_scope(self, query, organization_id: UUID | None, branch_id: UUID | None):
        if organization_id is not None:
            query = query.filter(Invoice.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Invoice.branch_id == branch_id)
        return query

    def _apply_payment_scope(self, query, organization_id: UUID | None, branch_id: UUID | None):
        if organization_id is not None:
            query = query.filter(Payment.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(Payment.branch_id == branch_id)
        return query
