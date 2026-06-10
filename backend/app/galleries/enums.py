from enum import StrEnum


class GalleryStatus(StrEnum):
    DRAFT = "DRAFT"
    UPLOADED = "UPLOADED"
    SELECTION_OPEN = "SELECTION_OPEN"
    SELECTION_CLOSED = "SELECTION_CLOSED"
