from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.integrations.models import OrganizationIntegration
from app.shared.pagination import PageResult, paginate_query


class IntegrationsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, integration: OrganizationIntegration) -> OrganizationIntegration:
        self.db.add(integration)
        return integration

    def get(self, integration_id: UUID) -> OrganizationIntegration | None:
        return self.db.get(OrganizationIntegration, integration_id)

    def get_by_scope(
        self,
        organization_id: UUID,
        branch_id: UUID | None,
        provider: str,
    ) -> OrganizationIntegration | None:
        return (
            self.db.query(OrganizationIntegration)
            .filter(
                OrganizationIntegration.organization_id == organization_id,
                OrganizationIntegration.branch_id == branch_id,
                OrganizationIntegration.provider == provider,
            )
            .one_or_none()
        )

    def list(
        self,
        *,
        page: int,
        page_size: int,
        organization_id: UUID | None,
        branch_id: UUID | None,
        provider: str | None = None,
        status: str | None = None,
    ) -> PageResult:
        query = self.db.query(OrganizationIntegration)
        if organization_id is not None:
            query = query.filter(OrganizationIntegration.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(OrganizationIntegration.branch_id == branch_id)
        if provider is not None:
            query = query.filter(OrganizationIntegration.provider == provider)
        if status is not None:
            query = query.filter(OrganizationIntegration.status == status)
        return paginate_query(
            query.order_by(
                OrganizationIntegration.provider.asc(),
                OrganizationIntegration.created_at.desc(),
            ),
            page,
            page_size,
        )

    def health(self, organization_id: UUID | None, branch_id: UUID | None) -> dict[str, int]:
        query = self.db.query(
            OrganizationIntegration.status, func.count(OrganizationIntegration.id)
        )
        if organization_id is not None:
            query = query.filter(OrganizationIntegration.organization_id == organization_id)
        if branch_id is not None:
            query = query.filter(OrganizationIntegration.branch_id == branch_id)
        rows = query.group_by(OrganizationIntegration.status).all()
        return {status.lower(): count for status, count in rows}
