from decimal import Decimal

from app.finance.models import Invoice, Payment


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _money(value: Decimal) -> str:
    return f"INR {value:.2f}"


def _simple_pdf(title: str, lines: list[str]) -> bytes:
    text_lines = [title, *lines]
    content = ["BT", "/F1 12 Tf", "50 780 Td"]
    for index, line in enumerate(text_lines):
        if index:
            content.append("0 -18 Td")
        content.append(f"({_escape_pdf_text(line)}) Tj")
    content.append("ET")
    stream = "\n".join(content).encode("utf-8")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(stream)).encode("ascii")
        + b" >>\nstream\n"
        + stream
        + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def invoice_pdf(invoice: Invoice) -> bytes:
    lines = [
        f"Invoice Number: {invoice.invoice_number}",
        f"Status: {invoice.invoice_status}",
        f"Issue Date: {invoice.issue_date or '-'}",
        f"Due Date: {invoice.due_date}",
        f"Seller: {invoice.seller_legal_name or '-'}",
        f"Seller GSTIN: {invoice.seller_gstin or '-'}",
        f"Buyer: {invoice.buyer_billing_name or '-'}",
        f"Buyer GSTIN: {invoice.buyer_gstin or '-'}",
        f"Supply Type: {invoice.supply_type}",
        f"Place Of Supply: {invoice.place_of_supply_state_code or '-'}",
        f"Taxable Amount: {_money(invoice.taxable_amount)}",
        f"CGST: {_money(invoice.cgst_amount)}",
        f"SGST: {_money(invoice.sgst_amount)}",
        f"IGST: {_money(invoice.igst_amount)}",
        f"Total: {_money(invoice.total_amount)}",
        f"Paid: {_money(invoice.amount_paid)}",
        f"Balance Due: {_money(invoice.balance_due)}",
    ]
    return _simple_pdf("GST Invoice", lines)


def payment_receipt_pdf(payment: Payment) -> bytes:
    lines = [
        f"Payment Number: {payment.payment_number}",
        f"Invoice ID: {payment.invoice_id}",
        f"Status: {payment.payment_status}",
        f"Method: {payment.payment_method}",
        f"Amount: {_money(payment.amount)}",
        f"Received Date: {payment.received_date}",
        f"Transaction Reference: {payment.transaction_reference or '-'}",
    ]
    return _simple_pdf("Payment Receipt", lines)
