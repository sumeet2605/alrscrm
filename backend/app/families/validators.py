import re

from app.shared.exceptions.application import ValidationError

_PHONE_ALLOWED = re.compile(r"^[0-9+\-\s()]{6,30}$")


def normalize_phone(value: str) -> str:
    normalized = " ".join(value.strip().split())
    if not _PHONE_ALLOWED.match(normalized):
        raise ValidationError("Phone number contains unsupported characters")
    return normalized


def format_family_code(sequence_value: int) -> str:
    return f"ALS-{sequence_value:06d}"
