from dataclasses import dataclass
from uuid import UUID

from app.identity.models import Branch, Organization, Role, User
from app.shared.exceptions.application import ForbiddenError


@dataclass(frozen=True)
class AuthorizationContext:
    user_id: UUID
    organization_id: UUID
    branch_id: UUID | None
    role_names: frozenset[str]
    permission_codes: frozenset[str]
    is_platform_admin: bool
    max_role_priority: int

    @classmethod
    def from_user(cls, user: User) -> "AuthorizationContext":
        roles = list(user.roles)
        return cls(
            user_id=user.id,
            organization_id=user.organization_id,
            branch_id=user.branch_id,
            role_names=frozenset(role.name for role in roles),
            permission_codes=frozenset(
                permission.code for role in roles for permission in role.permissions
            ),
            is_platform_admin=any(role.is_platform for role in roles),
            max_role_priority=max((role.priority for role in roles), default=0),
        )

    @property
    def is_owner(self) -> bool:
        return "Owner" in self.role_names or "Organization Admin" in self.role_names

    @property
    def is_branch_scoped(self) -> bool:
        return self.branch_id is not None and not self.is_platform_admin and not self.is_owner


def require_permission(context: AuthorizationContext, permission_code: str) -> None:
    if context.is_platform_admin:
        return
    if permission_code not in context.permission_codes:
        raise ForbiddenError("Insufficient permissions")


def can_access_organization(context: AuthorizationContext, organization: Organization) -> bool:
    return context.is_platform_admin or organization.id == context.organization_id


def ensure_can_access_organization(
    context: AuthorizationContext | None, organization: Organization
) -> None:
    if context is not None and not can_access_organization(context, organization):
        raise ForbiddenError("Organization is outside the caller scope")


def can_access_branch(context: AuthorizationContext, branch: Branch) -> bool:
    if context.is_platform_admin:
        return True
    if branch.organization_id != context.organization_id:
        return False
    if context.is_branch_scoped:
        return branch.id == context.branch_id
    return True


def ensure_can_access_branch(context: AuthorizationContext | None, branch: Branch) -> None:
    if context is not None and not can_access_branch(context, branch):
        raise ForbiddenError("Branch is outside the caller scope")


def can_access_user(context: AuthorizationContext, target_user: User) -> bool:
    if context.is_platform_admin:
        return True
    if target_user.organization_id != context.organization_id:
        return False
    if context.is_branch_scoped:
        return target_user.branch_id == context.branch_id or target_user.id == context.user_id
    return True


def ensure_can_access_user(context: AuthorizationContext | None, target_user: User) -> None:
    if context is not None and not can_access_user(context, target_user):
        raise ForbiddenError("User is outside the caller scope")


def ensure_can_assign_roles(context: AuthorizationContext | None, roles: list[Role]) -> None:
    if context is None:
        return
    for role in roles:
        if role.is_platform and not context.is_platform_admin:
            raise ForbiddenError("Only platform administrators can assign platform roles")
        if role.priority > context.max_role_priority:
            raise ForbiddenError("Cannot assign a role above the caller authority")
