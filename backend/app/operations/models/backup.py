from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BackupConfiguration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "backup_configurations"
    __table_args__ = (CheckConstraint("retention_days > 0", name="ck_backup_retention_positive"),)

    backup_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    backup_frequency: Mapped[str] = mapped_column(String(40), nullable=False, default="daily")
    retention_days: Mapped[int] = mapped_column(nullable=False, default=30)
    last_backup_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
