from enum import StrEnum


class OpportunityType(StrEnum):
    MATERNITY = "MATERNITY"
    NEWBORN = "NEWBORN"
    FAMILY = "FAMILY"
    MILESTONE = "MILESTONE"
    CAKE_SMASH = "CAKE_SMASH"


class OpportunityStage(StrEnum):
    NEW = "NEW"
    PACKAGE_SENT = "PACKAGE_SENT"
    INTERESTED = "INTERESTED"
    NEED_FOLLOW_UP = "NEED_FOLLOW_UP"
    THINKING = "THINKING"
    BOOKED = "BOOKED"
    LOST = "LOST"


class FollowUpType(StrEnum):
    CALL = "CALL"
    WHATSAPP = "WHATSAPP"
    INSTAGRAM_DM = "INSTAGRAM_DM"
    EMAIL = "EMAIL"
    OTHER = "OTHER"


class FollowUpStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
