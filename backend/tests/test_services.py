"""Tests for database service operations."""

from app.models.contact import ContactMessage
from app.models.project import Project
from app.models.story import Story
from app.schemas.contact import ContactMessageCreate
from app.schemas.project import ProjectCreate
from app.schemas.story import StoryCreate
from app.services.contact_service import ContactService
from app.services.project_service import ProjectService
from app.services.story_service import StoryService


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