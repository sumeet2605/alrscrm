from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.api.responses import api_response
from app.api.schemas import APIResponse
from app.core.database import get_db
from app.finance.enums import InvoiceStatus, PaymentMethod, PaymentStatus
from app.finance.pdf import invoice_pdf, payment_receipt_pdf
from app.finance.schemas import (
    FinanceMetricsRead,
    FinanceSettingsRead,
    FinanceSettingsUpdate,
    InvoiceCreate,
    InvoiceRead,
    InvoiceUpdate,
    PaymentCreate,
    PaymentRead,
)
from app.finance.services import finance_service

finance_router = APIRouter(prefix="/finance", tags=["Finance"])
invoices_router = APIRouter(prefix="/invoices", tags=["Invoices"])
payments_router = APIRouter(prefix="/payments", tags=["Payments"])


def _invoice(item) -> dict:
    return InvoiceRead.model_validate(item).model_dump(mode="json")


def _payment(item) -> dict:
    return PaymentRead.model_validate(item).model_dump(mode="json")


@finance_router.get("/settings", response_model=APIResponse)
def get_finance_settings(
    branch_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:view")),
):
    item = finance_service.get_settings(db, context, branch_id)
    return api_response(
        "Finance settings retrieved",
        FinanceSettingsRead.model_validate(item).model_dump(mode="json"),
    )


@finance_router.patch("/settings", response_model=APIResponse)
def update_finance_settings(
    payload: FinanceSettingsUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:update_invoice")),
):
    item = finance_service.update_settings(db, payload, context)
    return api_response(
        "Finance settings updated",
        FinanceSettingsRead.model_validate(item).model_dump(mode="json"),
    )


@finance_router.get("/metrics", response_model=APIResponse)
def get_finance_metrics(
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:dashboard")),
):
    metrics = FinanceMetricsRead(**finance_service.get_metrics(db, context))
    return api_response("Finance metrics retrieved", metrics.model_dump(mode="json"))


@invoices_router.get("", response_model=APIResponse)
def list_invoices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    branch_id: UUID | None = Query(default=None),
    invoice_status: InvoiceStatus | None = Query(default=None),
    booking_id: UUID | None = Query(default=None),
    family_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:view")),
):
    result = finance_service.list_invoices(
        db,
        context,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        invoice_status=invoice_status.value if invoice_status else None,
        booking_id=booking_id,
        family_id=family_id,
    )
    return api_response(
        "Invoices retrieved",
        [_invoice(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@invoices_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:create_invoice")),
):
    item = finance_service.create_invoice(db, payload, context)
    return api_response("Invoice created", _invoice(item))


@invoices_router.get("/{invoice_id}", response_model=APIResponse)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:view")),
):
    item = finance_service.get_invoice(db, invoice_id, context)
    return api_response("Invoice retrieved", _invoice(item))


@invoices_router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:view")),
):
    item = finance_service.get_invoice(db, invoice_id, context)
    return Response(
        content=invoice_pdf(item),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{item.invoice_number}.pdf"',
        },
    )


@invoices_router.put("/{invoice_id}", response_model=APIResponse)
def update_invoice(
    invoice_id: UUID,
    payload: InvoiceUpdate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:update_invoice")),
):
    item = finance_service.update_invoice(db, invoice_id, payload, context)
    return api_response("Invoice updated", _invoice(item))


@invoices_router.post("/{invoice_id}/issue", response_model=APIResponse)
def issue_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:update_invoice")),
):
    item = finance_service.issue_invoice(db, invoice_id, context)
    return api_response("Invoice issued", _invoice(item))


@invoices_router.post("/{invoice_id}/void", response_model=APIResponse)
def void_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:void_invoice")),
):
    item = finance_service.void_invoice(db, invoice_id, context)
    return api_response("Invoice voided", _invoice(item))


@payments_router.get("", response_model=APIResponse)
def list_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    branch_id: UUID | None = Query(default=None),
    payment_status: PaymentStatus | None = Query(default=None),
    payment_method: PaymentMethod | None = Query(default=None),
    invoice_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:view")),
):
    result = finance_service.list_payments(
        db,
        context,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        payment_status=payment_status.value if payment_status else None,
        payment_method=payment_method.value if payment_method else None,
        invoice_id=invoice_id,
    )
    return api_response(
        "Payments retrieved",
        [_payment(item) for item in result.items],
        meta=result.pagination.as_meta(),
    )


@payments_router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:create_payment")),
):
    item = finance_service.create_payment(db, payload, context)
    return api_response("Payment created", _payment(item))


@payments_router.get("/{payment_id}", response_model=APIResponse)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:view")),
):
    item = finance_service.get_payment(db, payment_id, context)
    return api_response("Payment retrieved", _payment(item))


@payments_router.get("/{payment_id}/receipt")
def download_payment_receipt(
    payment_id: UUID,
    db: Session = Depends(get_db),
    context=Depends(require_permissions("finance:view")),
):
    item = finance_service.get_payment(db, payment_id, context)
    return Response(
        content=payment_receipt_pdf(item),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{item.payment_number}-receipt.pdf"',
        },
    )
