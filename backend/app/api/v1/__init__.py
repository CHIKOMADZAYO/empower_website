"""API v1 routes module."""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.contact import router as contact_router
from app.api.v1.health import router as health_router
from app.api.v1.projects import router as projects_router
from app.api.v1.stories import router as stories_router


router = APIRouter(prefix="/api/v1")

# Register all routers
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(projects_router)
router.include_router(stories_router)
router.include_router(contact_router)

__all__ = ["router"]
