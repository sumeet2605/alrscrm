from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.core.database import Base
from app.families.models import Family
from app.identity.models import Branch, Organization, User
from app.shared.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class LostReason(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lost_reasons"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)


class Opportunity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunities"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "organization_id"],
            ["branches.id", "branches.organization_id"],
            name="fk_opportunity_branch_organization",
        ),
        CheckConstraint(
            "probability >= 0 AND probability <= 100",
            name="ck_opportunity_probability_range",
        ),
        CheckConstraint(
            "current_stage != 'LOST' OR lost_reason_id IS NOT NULL",
            name="ck_opportunity_lost_requires_reason",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("families.id"), nullable=False, index=True)
    assigned_to_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    opportunity_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    current_stage: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    estimated_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    probability: Mapped[int] = mapped_column(nullable=False, default=0)
    expected_booking_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    lost_reason_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("lost_reasons.id"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = sa_relationship(overlaps="branch")
    branch: Mapped[Branch] = sa_relationship(overlaps="organization")
    family: Mapped[Family] = sa_relationship()
    assigned_to_user: Mapped[User] = sa_relationship(foreign_keys=[assigned_to_user_id])
    lost_reason: Mapped[LostReason | None] = sa_relationship()
    followups: Mapped[list[FollowUp]] = sa_relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )
    opportunity_notes: Mapped[list[OpportunityNote]] = sa_relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )
    stage_history: Mapped[list[OpportunityStageHistory]] = sa_relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )


class FollowUp(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "followups"

    opportunity_id: Mapped[UUID] = mapped_column(
        ForeignKey("opportunities.id"), nullable=False, index=True
    )
    assigned_to_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    followup_type: Mapped[str] = mapped_column(String(40), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    opportunity: Mapped[Opportunity] = sa_relationship(back_populates="followups")
    assigned_to_user: Mapped[User] = sa_relationship()


class OpportunityNote(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "opportunity_notes"

    opportunity_id: Mapped[UUID] = mapped_column(
        ForeignKey("opportunities.id"), nullable=False, index=True
    )
    created_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    opportunity: Mapped[Opportunity] = sa_relationship(back_populates="opportunity_notes")
    created_by_user: Mapped[User] = sa_relationship()


class OpportunityStageHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "opportunity_stage_history"

    opportunity_id: Mapped[UUID] = mapped_column(
        ForeignKey("opportunities.id"), nullable=False, index=True
    )
    from_stage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    to_stage: Mapped[str] = mapped_column(String(40), nullable=False)
    changed_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    opportunity: Mapped[Opportunity] = sa_relationship(back_populates="stage_history")
    changed_by_user: Mapped[User] = sa_relationship()
