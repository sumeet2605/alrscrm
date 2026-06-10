from sqlalchemy.orm import Session

from app.identity.models import Permission, Role

ROLE_DEFINITIONS: tuple[tuple[str, str], ...] = (
    ("Super Admin", "Platform-wide administrative access."),
    ("Owner", "Full organization access across branches."),
    ("Branch Manager", "Full access within an assigned branch."),
    ("Sales Executive", "CRM, opportunity, and follow-up access."),
    ("Photographer", "Assigned session access."),
    ("Editor", "Assigned editing job access."),
    ("Customer Success", "Gallery, selection, and delivery access."),
    ("Client", "Client portal access."),
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
)

ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "Super Admin": tuple(code for code, _, _ in PERMISSION_DEFINITIONS),
    "Owner": tuple(code for code, _, _ in PERMISSION_DEFINITIONS),
    "Branch Manager": (
        "identity:branches:read",
        "identity:users:read",
        "identity:roles:read",
        "identity:permissions:read",
    ),
    "Sales Executive": ("identity:users:read", "identity:roles:read"),
    "Photographer": ("identity:users:read", "identity:roles:read"),
    "Editor": ("identity:users:read", "identity:roles:read"),
    "Customer Success": ("identity:users:read", "identity:roles:read"),
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
    for name, description in ROLE_DEFINITIONS:
        role = db.query(Role).filter(Role.name == name).one_or_none()
        if role is None:
            role = Role(name=name, description=description)
            db.add(role)
        roles_by_name[name] = role

    db.flush()

    for role_name, permission_codes in ROLE_PERMISSIONS.items():
        role = roles_by_name[role_name]
        desired = {permissions_by_code[code] for code in permission_codes}
        existing = set(role.permissions)
        for permission in desired - existing:
            role.permissions.append(permission)

    db.commit()
