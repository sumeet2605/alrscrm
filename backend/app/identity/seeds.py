from sqlalchemy.orm import Session

from app.identity.models import Permission, Role
from app.shared.exceptions.application import ValidationError

ROLE_DEFINITIONS: tuple[tuple[str, str, bool, int], ...] = (
    ("Super Admin", "Platform-wide administrative access.", True, 1000),
    ("Owner", "Full organization access across branches.", False, 900),
    ("Branch Manager", "Full access within an assigned branch.", False, 700),
    ("Sales Executive", "CRM, opportunity, and follow-up access.", False, 400),
    ("Photographer", "Assigned session access.", False, 300),
    ("Editor", "Assigned editing job access.", False, 300),
    ("Customer Success", "Gallery, selection, and delivery access.", False, 300),
    ("Client", "Client portal access.", False, 100),
)

PERMISSION_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    ("identity:organizations:read", "Read organizations", "View organizations."),
    ("identity:organizations:write", "Manage organizations", "Create and update organizations."),
    ("identity:branches:read", "Read branches", "View branches."),
    ("identity:branches:write", "Manage branches", "Create and update branches."),
    ("identity:users:read", "Read users", "View users."),
    ("identity:users:write", "Manage users", "Create and update users."),
    ("identity:roles:read", "Read roles", "View roles."),
    ("identity:permissions:read", "Read permissions", "View permissions."),
    ("families:read", "Read families", "View family CRM records."),
    ("families:write", "Manage families", "Create and update family CRM records."),
    ("families:delete", "Delete families", "Soft delete family CRM records."),
    ("sales:opportunities:read", "Read opportunities", "View sales opportunities."),
    ("sales:opportunities:write", "Manage opportunities", "Create and update opportunities."),
    ("sales:opportunities:delete", "Delete opportunities", "Soft delete opportunities."),
    ("sales:followups:read", "Read follow-ups", "View opportunity follow-ups."),
    ("sales:followups:write", "Manage follow-ups", "Create and update follow-ups."),
    ("sales:lost_reasons:read", "Read lost reasons", "View lost reason reference data."),
    ("bookings:read", "Read bookings", "View bookings and fulfillment data."),
    ("bookings:write", "Manage bookings", "Create and update bookings."),
    ("bookings:delete", "Delete bookings", "Soft delete bookings."),
    ("bookings:packages:read", "Read packages", "View package reference data."),
    ("bookings:packages:write", "Manage packages", "Create and update packages."),
    ("bookings:addons:read", "Read package addons", "View addon reference data."),
    ("bookings:addons:write", "Manage package addons", "Create and update addons."),
    ("bookings:schedules:read", "Read schedules", "View shoot schedules."),
    ("bookings:schedules:write", "Manage schedules", "Create and update shoot schedules."),
    ("bookings:assignments:read", "Read assignments", "View photographer assignments."),
    ("bookings:assignments:write", "Manage assignments", "Assign photographers."),
    ("galleries:read", "Read galleries", "View gallery management data."),
    ("galleries:write", "Manage galleries", "Create and update galleries."),
    ("galleries:photos:read", "Read gallery photos", "View gallery photos."),
    ("galleries:photos:write", "Manage gallery photos", "Upload and remove gallery photos."),
    ("galleries:favorites:read", "Read gallery favorites", "View favorite selections."),
    ("galleries:favorites:write", "Manage gallery favorites", "Create and remove favorites."),
)

ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "Super Admin": tuple(code for code, _, _ in PERMISSION_DEFINITIONS),
    "Owner": tuple(code for code, _, _ in PERMISSION_DEFINITIONS),
    "Branch Manager": (
        "identity:branches:read",
        "identity:users:read",
        "identity:roles:read",
        "identity:permissions:read",
        "families:read",
        "families:write",
        "families:delete",
        "sales:opportunities:read",
        "sales:opportunities:write",
        "sales:opportunities:delete",
        "sales:followups:read",
        "sales:followups:write",
        "sales:lost_reasons:read",
        "bookings:read",
        "bookings:write",
        "bookings:delete",
        "bookings:packages:read",
        "bookings:packages:write",
        "bookings:addons:read",
        "bookings:addons:write",
        "bookings:schedules:read",
        "bookings:schedules:write",
        "bookings:assignments:read",
        "bookings:assignments:write",
        "galleries:read",
        "galleries:write",
        "galleries:photos:read",
        "galleries:photos:write",
        "galleries:favorites:read",
        "galleries:favorites:write",
    ),
    "Sales Executive": (
        "identity:users:read",
        "identity:roles:read",
        "families:read",
        "families:write",
        "sales:opportunities:read",
        "sales:opportunities:write",
        "sales:followups:read",
        "sales:followups:write",
        "sales:lost_reasons:read",
        "bookings:read",
        "bookings:write",
        "bookings:packages:read",
        "bookings:addons:read",
        "bookings:schedules:read",
        "galleries:read",
        "galleries:photos:read",
    ),
    "Photographer": (
        "identity:users:read",
        "identity:roles:read",
        "families:read",
        "sales:opportunities:read",
        "sales:followups:read",
        "sales:lost_reasons:read",
        "bookings:read",
        "bookings:schedules:read",
        "bookings:assignments:read",
        "galleries:read",
        "galleries:photos:read",
        "galleries:photos:write",
    ),
    "Editor": (
        "identity:users:read",
        "identity:roles:read",
        "families:read",
        "sales:opportunities:read",
        "sales:followups:read",
        "sales:lost_reasons:read",
        "bookings:read",
        "bookings:schedules:read",
        "galleries:read",
        "galleries:photos:read",
    ),
    "Customer Success": (
        "identity:users:read",
        "identity:roles:read",
        "families:read",
        "sales:opportunities:read",
        "sales:followups:read",
        "sales:lost_reasons:read",
        "bookings:read",
        "bookings:schedules:read",
        "galleries:read",
        "galleries:photos:read",
        "galleries:favorites:read",
        "galleries:favorites:write",
    ),
    "Client": (),
}


def seed_identity(db: Session) -> None:
    permissions_by_code: dict[str, Permission] = {}
    for code, name, description in PERMISSION_DEFINITIONS:
        permission = db.query(Permission).filter(Permission.code == code).one_or_none()
        if permission is None:
            permission = Permission(code=code, name=name, description=description)
            db.add(permission)
        permissions_by_code[code] = permission

    roles_by_name: dict[str, Role] = {}
    for name, description, is_platform, priority in ROLE_DEFINITIONS:
        role = db.query(Role).filter(Role.name == name).one_or_none()
        if role is None:
            role = Role(
                name=name,
                description=description,
                is_platform=is_platform,
                priority=priority,
            )
            db.add(role)
        else:
            role.description = description
            role.is_platform = is_platform
            role.priority = priority
        roles_by_name[name] = role

    db.flush()

    for role_name, permission_codes in ROLE_PERMISSIONS.items():
        role = roles_by_name[role_name]
        desired = {permissions_by_code[code] for code in permission_codes}
        existing = set(role.permissions)
        for permission in desired - existing:
            role.permissions.append(permission)

    db.commit()


def validate_identity_seed(db: Session) -> None:
    role_count = db.query(Role).count()
    permission_count = db.query(Permission).count()
    if role_count < len(ROLE_DEFINITIONS) or permission_count < len(PERMISSION_DEFINITIONS):
        raise ValidationError("Identity roles and permissions have not been seeded")
