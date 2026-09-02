"""Contact message service - business logic for contact operations."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import ContactMessage
from app.schemas.contact import ContactMessageCreate, ContactMessageResponse


class ContactService:
    """Business logic for contact messages."""

    @staticmethod
    def create_message(
        database: Session,
        contact_data: ContactMessageCreate
    ) -> ContactMessageResponse:
        """Create and store contact message."""
        message = ContactMessage(
            name=contact_data.name,
            email=contact_data.email,
            message=contact_data.message,
        )
        database.add(message)
        database.commit()

        return ContactMessageResponse(
            message="Thank you. Your message has been received by the Empower team.",
            received_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def get_all_messages(database: Session) -> list[ContactMessage]:
        """Get all contact messages (admin only)."""
        return database.scalars(
            select(ContactMessage).order_by(ContactMessage.created_at.desc())
        ).all()

    @staticmethod
    def get_message_by_id(database: Session, message_id: int) -> ContactMessage | None:
        """Get contact message by ID."""
        return database.scalar(
            select(ContactMessage).where(ContactMessage.id == message_id)
        )
    @staticmethod
    def get_message_by_email(database: Session, email: str) -> list[ContactMessage]:
        """Get contact messages by email."""
        return database.scalars(
            select(ContactMessage).where(ContactMessage.email == email)
        ).all() 


    

    @staticmethod
    def delete_message(database: Session, message_id: int) -> None:
        """Delete contact message by ID."""
        message = database.scalar(
            select(ContactMessage).where(ContactMessage.id == message_id)
        )
        if message:
            database.delete(message)
            database.commit()

            