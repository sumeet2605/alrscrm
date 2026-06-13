from sqlalchemy.orm import Session

from app.bookings import models as booking_models  # noqa: F401
from app.sales.models import LostReason

LOST_REASON_DEFINITIONS: tuple[tuple[str, str], ...] = (
    ("Too Expensive", "Budget objection or package price is too high."),
    ("Need Spouse Approval", "Decision requires spouse or family approval."),
    ("Comparing Competitors", "Customer is evaluating other studios."),
    ("Not Ready Yet", "Customer is interested but not ready to book."),
    ("Stopped Responding", "Customer stopped responding after outreach."),
)


def seed_sales(db: Session) -> None:
    for name, description in LOST_REASON_DEFINITIONS:
        reason = db.query(LostReason).filter(LostReason.name == name).one_or_none()
        if reason is None:
            reason = LostReason(name=name, description=description, is_active=True)
            db.add(reason)
        else:
            reason.description = description
            reason.is_active = True
    db.commit()
