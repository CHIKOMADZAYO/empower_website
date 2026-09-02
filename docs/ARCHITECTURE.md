# Architecture

## Overview

Empower is a full-stack web application with a FastAPI backend and vanilla HTML/CSS frontend.

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application entry
│   ├── core/             # Core application logic
│   ├── api/              # API endpoints
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic services
├── tests/                # Unit and integration tests
├── scripts/              # Utility scripts
└── data/                 # Runtime data (SQLite, etc.)
```

### Key Components

1. **API Routes** (`app/api/v1/`)
   - `auth.py` - Authentication endpoints
   - `health.py` - Health check
   - `projects.py` - Project management
   - `stories.py` - Story management
   - `contact.py` - Contact form handling

2. **Data Models** (`app/models/`)
   - User authentication and profiles
   - Projects
   - Stories
   - Contacts

3. **Services** (`app/services/`)
   - Business logic for each domain
   - Database operations
   - External integrations

## Frontend Architecture

### Directory Structure

```
frontend/
├── public/               # Static assets
├── src/
│   ├── pages/           # HTML pages
│   ├── styles/          # CSS files
│   ├── scripts/         # JavaScript utilities
│   └── components/      # Reusable components
└── dist/                # Build output
```

### Key Components

1. **Pages** (`src/pages/`)
   - Standalone HTML pages
   - Each page handles its own styles

2. **Styles** (`src/styles/`)
   - Modular CSS files
   - Responsive design
   - Component styles

3. **Scripts** (`src/scripts/`)
   - `api.js` - API communication
   - `auth.js` - Authentication utilities
   - `utils.js` - Helper functions
   - `constants.js` - App constants

## Data Flow

1. **User Interaction** (Frontend)
   - User interacts with HTML interface
   - JavaScript event handlers trigger API calls

2. **API Request** (Frontend → Backend)
   - `api.js` makes HTTP requests to `/api/v1/*`
   - Includes authentication tokens

3. **Backend Processing** (FastAPI)
   - Route handler validates request
   - Service layer performs business logic
   - Database operations via SQLAlchemy

4. **Response** (Backend → Frontend)
   - JSON response with data or error
   - Frontend updates UI accordingly

## Authentication

- JWT-based authentication
- Tokens stored in local storage
- Automatic token refresh on 401 responses
- Secure password hashing with bcrypt

## Database

- SQLite for development
- SQLAlchemy ORM
- Database file: `backend/data/empower.db`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guidelines.
