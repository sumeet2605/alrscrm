from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.bookings.models import Booking
from app.families.models import Family
from app.finance.enums import GSTRegistrationType, InvoiceStatus, PaymentStatus
from app.finance.models import FinanceSettings, Invoice, InvoiceLineItem, Payment
from app.finance.repositories import FinanceRepository
from app.finance.schemas import FinanceSettingsUpdate, InvoiceCreate, InvoiceUpdate, PaymentCreate
from app.identity.models import Branch
from app.identity.policies import AuthorizationContext
from app.shared.exceptions.application import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.shared.pagination import PageResult
from app.shared.services.audit_service import record_audit_event


def _scope_filters(
    context: AuthorizationContext, branch_id: UUID | None = None
) -> tuple[UUID | None, UUID | None]:
    if context.is_platform_admin:
        return None, branch_id
    scoped_branch_id = branch_id
    if context.is_branch_scoped:
        if branch_id is not None and branch_id != context.branch_id:
            raise ForbiddenError("Finance branch is outside the caller scope")
        scoped_branch_id = context.branch_id
    return context.organization_id, scoped_branch_id


def _ensure_branch_scope(db: Session, context: AuthorizationContext, branch_id: UUID) -> Branch:
    branch = db.get(Branch, branch_id)
    if branch is None or not branch.is_active:
        raise NotFoundError("Branch not found")
    if not context.is_platform_admin:
        if branch.organization_id != context.organization_id:
            raise ForbiddenError("Branch is outside the caller scope")
        if context.is_branch_scoped and branch.id != context.branch_id:
            raise ForbiddenError("Branch is outside the caller scope")
    return branch


def _ensure_family_scope(db: Session, context: AuthorizationContext, family_id: UUID) -> Family:
    family = db.get(Family, family_id)
    if family is None or family.deleted_at is not None:
        raise NotFoundError("Family not found")
    if not context.is_platform_admin:
        if family.organization_id != context.organization_id:
            raise ForbiddenError("Family is outside the caller scope")
        if context.is_branch_scoped and family.branch_id != context.branch_id:
            raise ForbiddenError("Family is outside the caller scope")
    return family


def _ensure_booking_scope(db: Session, context: AuthorizationContext, booking_id: UUID) -> Booking:
    booking = db.get(Booking, booking_id)
    if booking is None or booking.deleted_at is not None:
        raise NotFoundError("Booking not found")
    if not context.is_platform_admin:
        if booking.organization_id != context.organization_id:
            raise ForbiddenError("Booking is outside the caller scope")
        if context.is_branch_scoped and booking.branch_id != context.branch_id:
            raise ForbiddenError("Booking is outside the caller scope")
    return booking


def _ensure_invoice_scope(context: AuthorizationContext, invoice: Invoice) -> None:
    if context.is_platform_admin:
        return
    if invoice.organization_id != context.organization_id:
        raise ForbiddenError("Invoice is outside the caller scope")
    if context.is_branch_scoped and invoice.branch_id != context.branch_id:
        raise ForbiddenError("Invoice is outside the caller scope")


def _line_from_payload(payload) -> InvoiceLineItem:
    base_amount = payload.quantity * payload.unit_price
    taxable_amount = base_amount - payload.discount_amount
    if taxable_amount < 0:
        raise ValidationError("Line item discount cannot exceed line amount")
    line_total = taxable_amount + payload.cgst_amount + payload.sgst_amount + payload.igst_amount
    return InvoiceLineItem(
        description=payload.description,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        discount_amount=payload.discount_amount,
        taxable_amount=taxable_amount,
        tax_rate=payload.tax_rate,
        cgst_rate=payload.cgst_rate,
        cgst_amount=payload.cgst_amount,
        sgst_rate=payload.sgst_rate,
        sgst_amount=payload.sgst_amount,
        igst_rate=payload.igst_rate,
        igst_amount=payload.igst_amount,
        line_total=line_total,
        service_type=payload.service_type,
        sac_code=payload.sac_code,
    )


def _apply_invoice_totals(invoice: Invoice) -> None:
    subtotal = sum((item.quantity * item.unit_price for item in invoice.line_items), Decimal("0"))
    discount = sum((item.discount_amount for item in invoice.line_items), Decimal("0"))
    taxable = sum((item.taxable_amount for item in invoice.line_items), Decimal("0"))
    cgst = sum((item.cgst_amount for item in invoice.line_items), Decimal("0"))
    sgst = sum((item.sgst_amount for item in invoice.line_items), Decimal("0"))
    igst = sum((item.igst_amount for item in invoice.line_items), Decimal("0"))
    total = taxable + cgst + sgst + igst
    invoice.subtotal = subtotal
    invoice.discount_amount = discount
    invoice.taxable_amount = taxable
    invoice.cgst_amount = cgst
    invoice.sgst_amount = sgst
    invoice.igst_amount = igst
    invoice.total_amount = total
    invoice.balance_due = total - invoice.amount_paid
    if invoice.balance_due < 0:
        raise ValidationError("Invoice balance cannot be negative")


def _apply_payment_status(invoice: Invoice) -> None:
    if invoice.invoice_status == InvoiceStatus.VOID.value:
        return
    if invoice.amount_paid <= 0:
        if invoice.invoice_status == InvoiceStatus.PAID.value:
            invoice.invoice_status = InvoiceStatus.ISSUED.value
        return
    if invoice.balance_due == 0:
        invoice.invoice_status = InvoiceStatus.PAID.value
    else:
        invoice.invoice_status = InvoiceStatus.PARTIALLY_PAID.value


def get_settings(
    db: Session, context: AuthorizationContext, branch_id: UUID | None = None
) -> FinanceSettings:
    repository = FinanceRepository(db)
    organization_id, scoped_branch_id = _scope_filters(context, branch_id)
    if scoped_branch_id is not None:
        branch = _ensure_branch_scope(db, context, scoped_branch_id)
        organization_id = branch.organization_id
    elif organization_id is None:
        organization_id = context.organization_id
    settings = repository.get_settings(organization_id, scoped_branch_id)
    if settings is not None:
        return settings
    legal_name = "Platform" if context.is_platform_admin else "Studio"
    if not context.is_platform_admin and getattr(context, "organization_id", None):
        legal_name = "Studio"
    settings = FinanceSettings(
        organization_id=organization_id,
        branch_id=scoped_branch_id,
        registration_type=GSTRegistrationType.UNREGISTERED.value,
        legal_name=legal_name,
        default_currency="INR",
        default_due_days=15,
        invoice_prefix="INV",
        auto_create_booking_invoice=False,
        require_payment_before_delivery=False,
    )
    repository.add_settings(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_settings(
    db: Session, payload: FinanceSettingsUpdate, context: AuthorizationContext
) -> FinanceSettings:
    settings = get_settings(db, context, payload.branch_id)
    for field, value in payload.model_dump(exclude_unset=True, exclude={"branch_id"}).items():
        if hasattr(value, "value"):
            value = value.value
        if field == "default_currency" and value is not None:
            value = value.upper()
        setattr(settings, field, value)
    record_audit_event(
        db,
        "finance.settings_updated",
        context.user_id,
        "FinanceSettings",
        settings.id,
        organization_id=settings.organization_id,
        branch_id=settings.branch_id,
    )
    db.commit()
    db.refresh(settings)
    return settings


def list_invoices(db: Session, context: AuthorizationContext, **kwargs) -> PageResult:
    organization_id, branch_id = _scope_filters(context, kwargs.pop("branch_id", None))
    return FinanceRepository(db).list_invoices(
        organization_id=organization_id,
        branch_id=branch_id,
        **kwargs,
    )


def get_invoice(db: Session, invoice_id: UUID, context: AuthorizationContext) -> Invoice:
    invoice = FinanceRepository(db).get_invoice(invoice_id)
    if invoice is None:
        raise NotFoundError("Invoice not found")
    _ensure_invoice_scope(context, invoice)
    return invoice


def create_invoice(db: Session, payload: InvoiceCreate, context: AuthorizationContext) -> Invoice:
    repository = FinanceRepository(db)
    branch = _ensure_branch_scope(db, context, payload.branch_id)
    family = _ensure_family_scope(db, context, payload.family_id)
    booking = _ensure_booking_scope(db, context, payload.booking_id)
    if payload.organization_id != branch.organization_id:
        raise ValidationError("Invoice organization must match branch")
    if family.organization_id != payload.organization_id or family.branch_id != payload.branch_id:
        raise ValidationError("Invoice family must match branch and organization")
    if booking.organization_id != payload.organization_id or booking.branch_id != payload.branch_id:
        raise ValidationError("Invoice booking must match branch and organization")
    if booking.family_id != payload.family_id:
        raise ValidationError("Invoice booking must belong to family")
    settings = repository.get_settings(payload.organization_id, payload.branch_id) or get_settings(
        db, context, payload.branch_id
    )
    invoice = Invoice(
        organization_id=payload.organization_id,
        branch_id=payload.branch_id,
        family_id=payload.family_id,
        booking_id=payload.booking_id,
        invoice_number=repository.next_invoice_number(settings.invoice_prefix),
        invoice_status=InvoiceStatus.DRAFT.value,
        amount_paid=Decimal("0"),
        currency=payload.currency.upper(),
        due_date=payload.due_date,
        notes=payload.notes,
        created_by_user_id=context.user_id,
        seller_legal_name=payload.seller_legal_name or settings.legal_name,
        seller_trade_name=payload.seller_trade_name or settings.trade_name,
        seller_gstin=payload.seller_gstin or settings.gstin,
        seller_address=payload.seller_address or settings.billing_address,
        seller_state_code=payload.seller_state_code or settings.billing_state_code,
        buyer_billing_name=payload.buyer_billing_name,
        buyer_gstin=payload.buyer_gstin,
        buyer_billing_address=payload.buyer_billing_address,
        buyer_state_code=payload.buyer_state_code,
        place_of_supply_state_code=payload.place_of_supply_state_code,
        supply_type=payload.supply_type.value,
        gst_registration_type=payload.gst_registration_type.value,
        reverse_charge_applicable=payload.reverse_charge_applicable,
    )
    invoice.line_items = [_line_from_payload(item) for item in payload.line_items]
    _apply_invoice_totals(invoice)
    repository.add_invoice(invoice)
    try:
        db.flush()
        record_audit_event(
            db,
            "invoice.created",
            context.user_id,
            "Invoice",
            invoice.id,
            metadata={"domain_event": "InvoiceCreated"},
            organization_id=invoice.organization_id,
            branch_id=invoice.branch_id,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Invoice number already exists") from exc
    return get_invoice(db, invoice.id, context)


def update_invoice(
    db: Session, invoice_id: UUID, payload: InvoiceUpdate, context: AuthorizationContext
) -> Invoice:
    repository = FinanceRepository(db)
    invoice = get_invoice(db, invoice_id, context)
    if invoice.invoice_status != InvoiceStatus.DRAFT.value:
        raise ConflictError("Only draft invoices can be edited")
    if invoice.payments:
        raise ConflictError("Invoice totals are immutable after payment exists")
    data = payload.model_dump(exclude_unset=True, exclude={"line_items"})
    for field, value in data.items():
        if hasattr(value, "value"):
            value = value.value
        if field == "currency" and value is not None:
            value = value.upper()
        setattr(invoice, field, value)
    if payload.line_items is not None:
        repository.replace_line_items(
            invoice,
            [_line_from_payload(item) for item in payload.line_items],
        )
    _apply_invoice_totals(invoice)
    record_audit_event(
        db,
        "invoice.updated",
        context.user_id,
        "Invoice",
        invoice.id,
        metadata={"domain_event": "InvoiceUpdated"},
        organization_id=invoice.organization_id,
        branch_id=invoice.branch_id,
    )
    db.commit()
    return get_invoice(db, invoice.id, context)


def issue_invoice(db: Session, invoice_id: UUID, context: AuthorizationContext) -> Invoice:
    invoice = get_invoice(db, invoice_id, context)
    if invoice.invoice_status != InvoiceStatus.DRAFT.value:
        raise ConflictError("Only draft invoices can be issued")
    invoice.invoice_status = InvoiceStatus.ISSUED.value
    invoice.issue_date = date.today()
    record_audit_event(
        db,
        "invoice.issued",
        context.user_id,
        "Invoice",
        invoice.id,
        metadata={"domain_event": "InvoiceIssued"},
        organization_id=invoice.organization_id,
        branch_id=invoice.branch_id,
    )
    db.commit()
    return get_invoice(db, invoice.id, context)


def void_invoice(db: Session, invoice_id: UUID, context: AuthorizationContext) -> Invoice:
    invoice = get_invoice(db, invoice_id, context)
    if any(payment.payment_status == PaymentStatus.COMPLETED.value for payment in invoice.payments):
        raise ConflictError("Invoices with completed payments cannot be voided")
    invoice.invoice_status = InvoiceStatus.VOID.value
    invoice.voided_at = datetime.now(UTC)
    record_audit_event(
        db,
        "invoice.voided",
        context.user_id,
        "Invoice",
        invoice.id,
        metadata={"domain_event": "InvoiceVoided"},
        organization_id=invoice.organization_id,
        branch_id=invoice.branch_id,
    )
    db.commit()
    return get_invoice(db, invoice.id, context)


def list_payments(db: Session, context: AuthorizationContext, **kwargs) -> PageResult:
    organization_id, branch_id = _scope_filters(context, kwargs.pop("branch_id", None))
    return FinanceRepository(db).list_payments(
        organization_id=organization_id,
        branch_id=branch_id,
        **kwargs,
    )


def get_payment(db: Session, payment_id: UUID, context: AuthorizationContext) -> Payment:
    payment = FinanceRepository(db).get_payment(payment_id)
    if payment is None:
        raise NotFoundError("Payment not found")
    if not context.is_platform_admin:
        if payment.organization_id != context.organization_id:
            raise ForbiddenError("Payment is outside the caller scope")
        if context.is_branch_scoped and payment.branch_id != context.branch_id:
            raise ForbiddenError("Payment is outside the caller scope")
    return payment


def create_payment(db: Session, payload: PaymentCreate, context: AuthorizationContext) -> Payment:
    repository = FinanceRepository(db)
    invoice = repository.get_invoice_for_update(payload.invoice_id)
    if invoice is None:
        raise NotFoundError("Invoice not found")
    _ensure_invoice_scope(context, invoice)
    if invoice.invoice_status == InvoiceStatus.VOID.value:
        raise ConflictError("Void invoices cannot receive payments")
    if payload.payment_status == PaymentStatus.COMPLETED and payload.amount > invoice.balance_due:
        raise ConflictError("Payment amount cannot exceed invoice balance")
    payment = Payment(
        organization_id=invoice.organization_id,
        branch_id=invoice.branch_id,
        invoice_id=invoice.id,
        payment_number=repository.next_payment_number(),
        amount=payload.amount,
        payment_method=payload.payment_method.value,
        payment_status=payload.payment_status.value,
        transaction_reference=payload.transaction_reference,
        received_date=payload.received_date,
        notes=payload.notes,
        received_by_user_id=context.user_id,
        created_at=datetime.now(UTC),
    )
    repository.add_payment(payment)
    if payload.payment_status == PaymentStatus.COMPLETED:
        invoice.amount_paid += payload.amount
        invoice.balance_due = invoice.total_amount - invoice.amount_paid
        _apply_payment_status(invoice)
    try:
        db.flush()
        record_audit_event(
            db,
            "payment.created",
            context.user_id,
            "Payment",
            payment.id,
            metadata={"domain_event": "PaymentCreated", "invoice_id": str(invoice.id)},
            organization_id=payment.organization_id,
            branch_id=payment.branch_id,
        )
        if payment.payment_status == PaymentStatus.COMPLETED.value:
            record_audit_event(
                db,
                "payment.completed",
                context.user_id,
                "Payment",
                payment.id,
                metadata={"domain_event": "PaymentCompleted", "invoice_id": str(invoice.id)},
                organization_id=payment.organization_id,
                branch_id=payment.branch_id,
            )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Payment number already exists") from exc
    return get_payment(db, payment.id, context)


def get_metrics(db: Session, context: AuthorizationContext) -> dict:
    organization_id, branch_id = _scope_filters(context)
    return FinanceRepository(db).metrics(organization_id, branch_id)
