"""Contact message routes."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import UserRole
from app.core.security import require_roles
from app.models.user import User
from app.schemas.contact import (
    ContactMessageCreate,
    ContactMessageListResponse,
    ContactMessageResponse,
)
from app.services.contact_service import ContactService
from app.services.logs_service import record_activity_in_background

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_message(
    request: Request,
    background_tasks: BackgroundTasks,
    contact_data: ContactMessageCreate,
    database: Annotated[Session, Depends(get_db)],
) -> ContactMessageResponse:
    """Submit contact form message."""
    response = ContactService.create_message(database, contact_data)
    background_tasks.add_task(
        record_activity_in_background,
        user_id=None,
        action="USER SENT A MESSAGE",
        resource="contact_message",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return response


@router.get("", response_model=list[ContactMessageListResponse])
async def list_contact_messages(
    request: Request,
    background_tasks: BackgroundTasks,
    database: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> list[ContactMessageListResponse]:
    """Get all contact messages (admin only)."""
    messages = ContactService.get_all_messages(database)

    background_tasks.add_task(
        record_activity_in_background,
        user_id=current_user.id,
        action="ADMIN LISTS ALL MESSAGE",
        resource="contact_message",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return [ContactMessageListResponse.model_validate(m) for m in messages]


@router.get("/{message_id}", response_model=ContactMessageListResponse)
async def get_contact_message(
    message_id: int,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> ContactMessageListResponse:
    """Get contact message by ID (admin only)."""
    message = ContactService.get_message_by_id(database, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return ContactMessageListResponse.model_validate(message)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_message(
    message_id: int,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> Response:
    """Delete contact message by ID (admin only)."""
    if not ContactService.delete_message(database, message_id):
        raise HTTPException(status_code=404, detail="Message not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
