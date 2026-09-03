"""Tests for database service operations."""

from types import SimpleNamespace

import pytest

from app.models.contact import ContactMessage
from app.models.project import Project
from app.models.story import Story
from app.schemas.contact import ContactMessageCreate
from app.schemas.project import ProjectCreate
from app.schemas.story import StoryCreate
from app.services.contact_service import ContactService
from app.services.project_service import ProjectService
from app.services.story_service import StoryService
from app.services import auth_service


@pytest.mark.asyncio
async def test_welcome_email_retries_transient_smtp_failure(monkeypatch) -> None:
    attempts = 0

    async def send_email(subject, recipients, body):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("temporary SMTP failure")

    settings = SimpleNamespace(
        MAIL_ENABLED=True,
        MAIL_USERNAME="sender@example.com",
        MAIL_PASSWORD="password",
        MAIL_FROM="sender@example.com",
        MAIL_SERVER="smtp.example.com",
        MAIL_PORT=587,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        MAIL_RETRY_ATTEMPTS=3,
        MAIL_RETRY_DELAY_SECONDS=0,
    )
    monkeypatch.setattr(auth_service, "get_settings", lambda: settings)
    monkeypatch.setattr(auth_service, "Mail", lambda settings: SimpleNamespace(send_email=send_email))

    user = SimpleNamespace(username="newuser", email="newuser@example.com")
    await auth_service.AuthService.send_welcome_email(user)

    assert attempts == 3


def test_project_service_updates_and_deletes_projects(test_db) -> None:
    project = ProjectService.create_project(
        test_db,
        ProjectCreate(
            name="Original project",
            category="Education",
            summary="An original project summary.",
            description="A sufficiently long description for the original project.",
        ),
    )
    updated = ProjectService.update_project(
        test_db,
        project.id,
        ProjectCreate(
            name="Updated project",
            category="Health",
            summary="An updated project summary.",
            description="A sufficiently long description for the updated project.",
        ),
    )

    assert updated.name == "Updated project"
    assert ProjectService.update_project(test_db, 9999, ProjectCreate(
        name="Missing project", category="Health", summary="Missing summary.",
        description="A sufficiently long description for a missing project.",
    )) is None

    ProjectService.delete_project(test_db, project.id)
    assert ProjectService.get_project_by_id(test_db, project.id) is None
    ProjectService.delete_project(test_db, 9999)


def test_story_service_updates_and_deletes_stories(test_db) -> None:
    story = StoryService.create_story(
        test_db,
        StoryCreate(
            title="Original story",
            category="Learning",
            excerpt="An original story excerpt that is long enough.",
            year=2024,
        ),
    )
    updated = StoryService.update_story(
        test_db,
        story.id,
        StoryCreate(
            title="Updated story",
            category="Opportunity",
            excerpt="An updated story excerpt that is long enough.",
            year=2025,
        ),
    )

    assert updated.title == "Updated story"
    assert StoryService.update_story(test_db, 9999, StoryCreate(
        title="Missing story", category="Learning", excerpt="A missing story excerpt that is long enough.", year=2025,
    )) is None

    StoryService.delete_story(test_db, story.id)
    assert StoryService.get_story_by_id(test_db, story.id) is None
    StoryService.delete_story(test_db, 9999)


def test_contact_service_filters_and_deletes_messages(test_db) -> None:
    first = ContactService.create_message(
        test_db,
        ContactMessageCreate(
            name="First Person",
            email="same@example.com",
            message="The first contact message is long enough to be valid.",
        ),
    )
    test_db.add(ContactMessage(
        name="Second Person",
        email="same@example.com",
        message="The second contact message is also long enough to be valid.",
    ))
    test_db.commit()

    messages = ContactService.get_message_by_email(test_db, "same@example.com")
    assert len(messages) == 2
    stored = ContactService.get_all_messages(test_db)
    message_id = stored[0].id

    assert ContactService.get_message_by_id(test_db, message_id) is not None
    assert ContactService.get_message_by_id(test_db, 9999) is None
    ContactService.delete_message(test_db, message_id)
    ContactService.delete_message(test_db, 9999)
    assert ContactService.get_message_by_id(test_db, message_id) is None
    assert first.message.startswith("Thank you")