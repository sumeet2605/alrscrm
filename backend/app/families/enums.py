from enum import StrEnum


class FamilyStatus(StrEnum):
    INQUIRY = "INQUIRY"
    INTERESTED = "INTERESTED"
    BOOKED = "BOOKED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class LeadSource(StrEnum):
    INSTAGRAM = "INSTAGRAM"
    WHATSAPP = "WHATSAPP"
    GOOGLE = "GOOGLE"
    REFERRAL = "REFERRAL"
    WEBSITE = "WEBSITE"
    WALKIN = "WALKIN"
    OTHER = "OTHER"


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class Relationship(StrEnum):
    MOTHER = "MOTHER"
    FATHER = "FATHER"
    BABY = "BABY"
    GRANDPARENT = "GRANDPARENT"
    SIBLING = "SIBLING"
    OTHER = "OTHER"


class ServiceType(StrEnum):
    MATERNITY = "MATERNITY"
    NEWBORN = "NEWBORN"
    FAMILY = "FAMILY"
    MILESTONE = "MILESTONE"
    CAKE_SMASH = "CAKE_SMASH"
