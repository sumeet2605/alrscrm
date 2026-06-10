from enum import StrEnum


class EditingPriority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class EditingStatus(StrEnum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    READY_FOR_DELIVERY = "READY_FOR_DELIVERY"


class EditingReviewStatus(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
