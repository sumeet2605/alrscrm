from fastapi import APIRouter

from app.auth.routes import router as auth_router
from app.bookings.routes import (
    addons_router,
    assignments_router,
    bookings_router,
    packages_router,
    schedules_router,
)
from app.families.routes import router as families_router
from app.identity.routes.branches import router as branches_router
from app.identity.routes.organizations import router as organizations_router
from app.identity.routes.rbac import router as rbac_router
from app.identity.routes.users import router as users_router
from app.sales.routes import followups_router, lost_reasons_router, opportunities_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(organizations_router)
api_router.include_router(branches_router)
api_router.include_router(users_router)
api_router.include_router(rbac_router)
api_router.include_router(families_router)
api_router.include_router(opportunities_router)
api_router.include_router(followups_router)
api_router.include_router(lost_reasons_router)
api_router.include_router(bookings_router)
api_router.include_router(packages_router)
api_router.include_router(addons_router)
api_router.include_router(schedules_router)
api_router.include_router(assignments_router)
