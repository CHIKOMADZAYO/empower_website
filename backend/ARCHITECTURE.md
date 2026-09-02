"""Project structure documentation."""

# Empower Backend - Professional Scalable Architecture

## Directory Structure

```
backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory
│   ├── core/                     # Core infrastructure
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration & environment
│   │   ├── security.py           # Authentication & password hashing
│   │   └── database.py           # Database connection & session
│   ├── models/                   # SQLAlchemy domain models
│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   ├── project.py            # Project model
│   │   ├── story.py              # Story model
│   │   └── contact.py            # Contact message model
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py               # Auth schemas
│   │   ├── user.py               # User schemas
│   │   ├── project.py            # Project schemas
│   │   ├── story.py              # Story schemas
│   │   └── contact.py            # Contact schemas
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Auth business logic
│   │   ├── project_service.py    # Project business logic
│   │   ├── story_service.py      # Story business logic
│   │   └── contact_service.py    # Contact business logic
│   └── api/                      # API routes (versioned)
│       ├── __init__.py
│       └── v1/                   # API v1
│           ├── __init__.py
│           ├── auth.py           # Auth endpoints
│           ├── health.py         # Health check endpoints
│           ├── projects.py       # Project endpoints
│           ├── stories.py        # Story endpoints
│           └── contact.py        # Contact endpoints
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & configuration
│   └── test_auth.py             # Auth tests
├── main.py                       # Entry point (uvicorn)
├── requirements.txt              # Python dependencies
└── empower.db                    # SQLite database (generated)
```

## Architecture Layers

### 1. **Core Layer** (`app/core/`)
- **config.py**: Environment configuration and settings
- **security.py**: JWT auth, password hashing, OAuth2 scheme
- **database.py**: Database connection, session factory, Base class

### 2. **Models Layer** (`app/models/`)
Domain models representing database tables:
- User, Project, Story, ContactMessage
- One file per model for clarity and maintainability
- SQLAlchemy with type-mapped columns

### 3. **Schemas Layer** (`app/schemas/`)
Pydantic models for request/response validation:
- Input validation (e.g., SignupRequest)
- Output serialization (e.g., UserResponse)
- Organized by domain (auth, user, project, etc.)

### 4. **Services Layer** (`app/services/`)
Business logic isolated from routes:
- AuthService: User creation, authentication
- ProjectService: Project CRUD operations
- StoryService: Story management
- ContactService: Contact message handling

### 5. **API Layer** (`app/api/v1/`)
Route handlers using dependency injection:
- Each domain has its own router file
- Services handle business logic
- Controllers are thin and focused on HTTP concerns
- Versioned routes (v1) for future API versions

### 6. **Main** (`app/main.py`)
- FastAPI app factory pattern
- Middleware configuration (CORS)
- Lifespan context manager (startup/shutdown)
- Database initialization and seeding

## Key Design Patterns

### Dependency Injection
```python
from typing import Annotated
from fastapi import Depends
from app.core.database import get_db

async def get_projects(
    database: Annotated[Session, Depends(get_db)]
):
    return ProjectService.get_all_projects(database)
```

### Service Layer
```python
# Routes stay thin, business logic in services
async def create_project(
    project: ProjectCreate,
    database: Session
):
    return ProjectService.create_project(database, project)
```

### Authentication
```python
from typing import Annotated
from app.core.security import get_current_user, require_roles

async def admin_only(
    current_user: Annotated[User, Depends(require_roles("admin"))]
):
    pass
```

## Running the Application

### Development
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Production
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Database

SQLite by default, configurable via `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost/empower"
```

## Testing

```bash
pytest                    # Run all tests
pytest -v                # Verbose output
pytest tests/test_auth.py # Run specific test file
pytest -k "login"        # Run tests matching pattern
```

## Adding New Features

### 1. Create Model
```python
# app/models/new_domain.py
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class NewModel(Base):
    __tablename__ = "new_models"
    id: Mapped[int] = mapped_column(primary_key=True)
    ...
```

### 2. Create Schema
```python
# app/schemas/new_domain.py
from pydantic import BaseModel

class NewModelResponse(BaseModel):
    id: int
    ...
```

### 3. Create Service
```python
# app/services/new_service.py
class NewService:
    @staticmethod
    def get_all(database: Session):
        return database.scalars(...).all()
```

### 4. Create Routes
```python
# app/api/v1/new_domain.py
from fastapi import APIRouter
router = APIRouter(prefix="/new-domain", tags=["new"])

@router.get("")
async def list_items(database: Session = Depends(get_db)):
    return NewService.get_all(database)
```

### 5. Register Router
```python
# app/api/v1/__init__.py
router.include_router(new_router)
```

## Environment Variables

`.env` file (create from `.env.example`):
```
EMPOWER_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./empower.db
DEBUG=False
```

## API Endpoints

### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/public` - Public message

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/signup` - Register
- `GET /api/v1/auth/profile` - Get profile (requires auth)

### Projects
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project
- `POST /api/v1/projects` - Create project

### Stories
- `GET /api/v1/stories` - List stories
- `GET /api/v1/stories/{id}` - Get story
- `POST /api/v1/stories` - Create story

### Contact
- `POST /api/v1/contact` - Submit contact form
- `GET /api/v1/contact` - List messages (admin only)
- `GET /api/v1/contact/{id}` - Get message (admin only)

## Next Steps

1. **Environment Configuration**: Create `.env` file with your settings
2. **Database Migration**: Consider Alembic for schema migrations in production
3. **Testing**: Add more test coverage (integration, e2e tests)
4. **Logging**: Add structured logging with Python logging
5. **Error Handling**: Implement custom exception classes
6. **API Documentation**: Auto-generated Swagger/OpenAPI docs at `/docs`
7. **Rate Limiting**: Add rate limiting for public endpoints
8. **Caching**: Implement caching strategy (Redis for scaling)
