"""Health check routes."""
from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "empower-api"}


@router.get("/public")
async def public_message() -> dict[str, str]:
    """Public message endpoint."""
    return {"message": "Welcome to Empower API"}
