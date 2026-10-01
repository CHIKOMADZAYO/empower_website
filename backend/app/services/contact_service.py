"""Contact message service - business logic for contact operations."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import ContactMessage
from app.schemas.contact import ContactMessageCreate, ContactMessageResponse


class ContactService:
    """Business logic for contact messages."""

    @staticmethod
    def create_message(
        database: Session, contact_data: ContactMessageCreate
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
            received_at=datetime.now(UTC),
        )

    @staticmethod
    def get_all_messages(database: Session) -> list[ContactMessage]:
        """Get all contact messages (admin only)."""
        rows = database.scalars(
            select(ContactMessage).order_by(ContactMessage.created_at.desc())
        ).all()
        return list(rows)

    @staticmethod
    def get_message_by_id(database: Session, message_id: int) -> ContactMessage | None:
        """Get contact message by ID."""
        return database.scalar(select(ContactMessage).where(ContactMessage.id == message_id))

    @staticmethod
    def get_message_by_email(database: Session, email: str) -> list[ContactMessage]:
        """Get contact messages by email."""
        rows = database.scalars(select(ContactMessage).where(ContactMessage.email == email)).all()
        return list(rows)

    @staticmethod
    def delete_message(database: Session, message_id: int) -> bool:
        """Delete contact message by ID, returning whether it existed."""
        message = database.scalar(select(ContactMessage).where(ContactMessage.id == message_id))
        if not message:
            return False
        database.delete(message)
        database.commit()
        return True
