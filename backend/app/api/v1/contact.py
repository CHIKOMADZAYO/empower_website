"""Contact message routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.contact import (
    ContactMessageCreate,
    ContactMessageListResponse,
    ContactMessageResponse,
)
from app.services.contact_service import ContactService


router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_message(
    contact_data: ContactMessageCreate,
    database: Annotated[Session, Depends(get_db)],
) -> ContactMessageResponse:
    """Submit contact form message."""
    return ContactService.create_message(database, contact_data)


@router.get("", response_model=list[ContactMessageListResponse])
async def list_contact_messages(
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> list[ContactMessageListResponse]:
    """Get all contact messages (admin only)."""
    messages = ContactService.get_all_messages(database)
    return [
        ContactMessageListResponse.model_validate(m) for m in messages
    ]


@router.get("/{message_id}", response_model=ContactMessageListResponse)
async def get_contact_message(
    message_id: int,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> ContactMessageListResponse:
    """Get contact message by ID (admin only)."""
    message = ContactService.get_message_by_id(database, message_id)
    if not message:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Message not found")
    return ContactMessageListResponse.model_validate(message)
