from enum import StrEnum


class GSTRegistrationType(StrEnum):
    REGULAR = "REGULAR"
    COMPOSITION = "COMPOSITION"
    EXEMPT = "EXEMPT"
    UNREGISTERED = "UNREGISTERED"


class SupplyType(StrEnum):
    INTRA_STATE = "INTRA_STATE"
    INTER_STATE = "INTER_STATE"
    NON_GST = "NON_GST"


class InvoiceStatus(StrEnum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    VOID = "VOID"
    OVERDUE = "OVERDUE"


class PaymentMethod(StrEnum):
    CASH = "CASH"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"
    CHEQUE = "CHEQUE"
    OTHER = "OTHER"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
