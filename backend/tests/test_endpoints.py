"""Integration tests for public and protected API endpoints."""

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import create_access_token, hash_password
from app.models.project import Project
from app.models.story import Story
from app.models.user import User


def test_public_health_endpoints(client: TestClient) -> None:
    """Public health routes should be reachable without auth."""
    health_response = client.get("/api/v1/health")
    assert health_response.status_code == 200, health_response.text
    assert health_response.json()["status"] == "ok"

    public_response = client.get("/api/v1/public")
    assert public_response.status_code == 200, public_response.text
    assert public_response.json()["message"] == "Welcome to Empower API"


def test_projects_endpoints(client: TestClient) -> None:
    """Projects should list, return details, and allow creation."""
    with SessionLocal() as db:
        db.add(
            Project(
                name="Community Mentoring",
                category="Education",
                summary="Support young people as they grow into local leaders.",
                description="This project provides mentoring, workshops, and practical opportunities for young people to grow leadership skills within their communities.",
            )
        )
        db.commit()

    list_response = client.get("/api/v1/projects")
    assert list_response.status_code == 200, list_response.text
    projects = list_response.json()
    assert len(projects) >= 1

    project_id = projects[0]["id"]
    detail_response = client.get(f"/api/v1/projects/{project_id}")
    assert detail_response.status_code == 200, detail_response.text
    assert detail_response.json()["id"] == project_id

    missing_response = client.get("/api/v1/projects/999999")
    assert missing_response.status_code == 404, missing_response.text

    payload = {
        "name": "Youth Leadership",
        "category": "Education",
        "summary": "Support the next generation of community leaders.",
        "description": "A six-month mentoring programme helping young people build confidence, advocacy, and practical skills for local leadership roles.",
    }
    create_response = client.post("/api/v1/projects", json=payload)
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["name"] == payload["name"]
    assert created["category"] == payload["category"]


def test_stories_endpoints(client: TestClient) -> None:
    """Stories should list, return details, and allow creation."""
    with SessionLocal() as db:
        db.add(
            Story(
                title="The garden became our classroom.",
                category="Wellbeing",
                excerpt="A community garden became a place for families to learn practical skills, share food, and grow connection.",
                year=2025,
            )
        )
        db.commit()

    list_response = client.get("/api/v1/stories")
    assert list_response.status_code == 200, list_response.text
    stories = list_response.json()
    assert len(stories) >= 1

    story_id = stories[0]["id"]
    detail_response = client.get(f"/api/v1/stories/{story_id}")
    assert detail_response.status_code == 200, detail_response.text
    assert detail_response.json()["id"] == story_id

    missing_response = client.get("/api/v1/stories/999999")
    assert missing_response.status_code == 404, missing_response.text

    payload = {
        "title": "Our community garden grew into a learning hub.",
        "category": "Wellbeing",
        "excerpt": "A small plot of land became a place where families learned, shared food, and built stronger neighbourhood ties.",
        "year": 2024,
    }
    create_response = client.post("/api/v1/stories", json=payload)
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["title"] == payload["title"]
    assert created["category"] == payload["category"]


def test_contact_endpoints(client: TestClient) -> None:
    """Contact form submissions should work and admin users can read them."""
    payload = {
        "name": "Nadia Smith",
        "email": "nadia@example.com",
        "message": "We would like to partner with your team on a youth wellbeing initiative in the local community.",
    }

    create_response = client.post("/api/v1/contact", json=payload)
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["message"] == "Thank you. Your message has been received by the Empower team."

    with SessionLocal() as db:
        admin = User(
            username="admin_contact_user",
            email="admin_contact@example.com",
            hashed_password=hash_password("StrongPass123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        token = create_access_token(admin)

    headers = {"Authorization": f"Bearer {token}"}

    list_response = client.get("/api/v1/contact", headers=headers)
    assert list_response.status_code == 200, list_response.text
    messages = list_response.json()
    assert any(item["email"] == payload["email"] for item in messages)

    first_message = messages[0]
    detail_response = client.get(
        f"/api/v1/contact/{first_message['id']}",
        headers=headers,
    )
    assert detail_response.status_code == 200, detail_response.text
    assert detail_response.json()["email"] == first_message["email"]


def test_protected_endpoints_reject_unauthorized_and_forbidden_access(client: TestClient) -> None:
    """Protected contact routes should reject missing or insufficient auth."""
    no_token_response = client.get("/api/v1/contact")
    assert no_token_response.status_code == 401, no_token_response.text

    with SessionLocal() as db:
        viewer = User(
            username="viewer_contact_user",
            email="viewer_contact@example.com",
            hashed_password=hash_password("StrongPass123"),
            role="viewer",
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)
        token = create_access_token(viewer)

    headers = {"Authorization": f"Bearer {token}"}
    forbidden_response = client.get("/api/v1/contact", headers=headers)
    assert forbidden_response.status_code == 403, forbidden_response.text
