# Project Structure Guide

This document describes the professional folder structure for the Empower project.

## Root Level

```
.editorconfig           # Editor configuration for consistency
.env.example            # Template for environment variables
.gitignore              # Git ignore patterns
.github/                # GitHub specific files
  workflows/            # CI/CD workflows
docker-compose.yml      # Docker compose configuration
LICENSE                 # Project license
README.md               # Project overview and quick start
docs/                   # Project documentation
```

## Backend (`backend/`)

### Structure
```
backend/
├── .env                # Environment variables (gitignored)
├── .env.example        # Environment template
├── .gitignore          # Python-specific gitignore
├── .venv/              # Python virtual environment
├── pytest.ini          # Pytest configuration
├── requirements.txt    # Python dependencies
├── app/                # Main application package
│   ├── main.py         # FastAPI application entry point
│   ├── core/           # Core functionality
│   │   ├── config.py   # Configuration management
│   │   ├── database.py # Database setup
│   │   └── security.py # Security utilities
│   ├── api/            # API endpoints
│   │   └── v1/         # API v1 routes
│   │       ├── auth.py
│   │       ├── contact.py
│   │       ├── health.py
│   │       ├── projects.py
│   │       └── stories.py
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic validation schemas
│   └── services/       # Business logic services
├── tests/              # Test suite
│   ├── conftest.py     # Pytest configuration
│   ├── fixtures/       # Test fixtures
│   └── test_*.py       # Test files
├── scripts/            # Utility scripts
│   ├── seed_db.py      # Database seeding
│   └── migrate.py      # Database migrations
└── data/               # Runtime data (gitignored)
    └── *.db            # SQLite database files
```

### Key Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Routes in `api/v1/`**: Easy versioning for future API versions
- **Services Layer**: Business logic isolated from HTTP layer
- **Models**: Database models in dedicated folder
- **Schemas**: Request/response validation in dedicated folder
- **Tests**: Mirror application structure
- **Data**: Database files isolated in data/ folder

## Frontend (`frontend/`)

### Structure
```
frontend/
├── .env                # Environment variables (gitignored)
├── .env.example        # Environment template
├── .gitignore          # Frontend-specific gitignore
├── package.json        # Node.js dependencies and scripts
├── vite.config.js      # Vite build configuration
├── public/             # Static assets (not bundled)
│   ├── favicon.ico
│   ├── images/
│   ├── icons/
│   └── fonts/
├── src/                # Source code
│   ├── main.js         # Entry point
│   ├── pages/          # HTML pages
│   │   ├── index.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── donate.html
│   │   ├── login.html
│   │   ├── projects.html
│   │   ├── signup.html
│   │   ├── stories.html
│   │   └── support.html
│   ├── styles/         # CSS files
│   │   ├── index.css        # Main stylesheet
│   │   ├── main.css         # Migrated from root style.css
│   │   ├── components.css   # Component styles
│   │   ├── responsive.css   # Responsive design
│   │   └── variables.css    # CSS variables
│   ├── scripts/        # JavaScript modules
│   │   ├── api.js      # API communication
│   │   ├── auth.js     # Authentication
│   │   ├── constants.js # App constants
│   │   └── utils.js    # Utility functions
│   └── components/     # Reusable components (for future framework migration)
└── dist/               # Build output (gitignored)
```

### Key Principles

- **Public Folder**: Static assets that aren't bundled
- **Pages**: Separate HTML files for each route
- **Styles**: Modular CSS with variables and components
- **Scripts**: Utility modules for common functionality
- **Vite**: Modern build tool for fast development

## Documentation (`docs/`)

```
docs/
├── ARCHITECTURE.md     # System architecture overview
├── SETUP.md            # Development setup guide
├── API.md              # API endpoint documentation
└── DEPLOYMENT.md       # Production deployment guide
```

## File Organization Principles

### Python Files
- `__init__.py`: Makes directory a package
- `main.py`: Entry point for applications/modules
- `conftest.py`: Pytest configuration and fixtures
- `test_*.py`: Test files following pytest conventions

### JavaScript Files
- `main.js`: Application entry point
- `api.js`: API utilities
- `auth.js`: Authentication utilities
- `utils.js`: Helper functions
- `constants.js`: App constants
- `*.css`: Component and style files

### Configuration Files
- `.env`: Environment variables (gitignored)
- `.env.example`: Environment template (committed)
- `.gitignore`: Git ignore patterns
- `pytest.ini`: Pytest configuration
- `vite.config.js`: Vite build configuration

## Moving Between Old and New Structure

### Files to Delete (Already have better versions in app/)
- `backend/auth.py` (duplicate of app/api/v1/auth.py)
- `backend/database.py` (duplicate of app/core/database.py)
- `backend/models.py` (duplicate of app/models/)
- `backend/schemas.py` (duplicate of app/schemas/)
- `backend/__init__.py` (moved to backend/app/)

### Files to Move
- `backend/test_*.py` → `backend/tests/`
- `backend/run_*.py` → `backend/scripts/` (as utilities)
- `backend/direct_test_run.py` → `backend/scripts/`
- `backend/manual_test_run.py` → `backend/scripts/`
- `backend/save_test_results.py` → `backend/scripts/`
- `frontend/*.html` → `frontend/src/pages/`
- `frontend/style.css` → `frontend/src/styles/main.css`
- `frontend/scripts/api.js` → `frontend/src/scripts/api.js`

### Created Files
- `.github/workflows/backend-tests.yml`
- `.github/workflows/frontend-build.yml`
- `docs/ARCHITECTURE.md`
- `docs/SETUP.md`
- `docs/API.md`
- `docs/DEPLOYMENT.md`
- `backend/pytest.ini`
- `backend/scripts/seed_db.py`
- `backend/scripts/migrate.py`
- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/styles/index.css`
- `frontend/src/styles/components.css`
- `frontend/src/styles/responsive.css`
- `frontend/src/styles/variables.css`
- `frontend/src/scripts/auth.js`
- `frontend/src/scripts/utils.js`
- `frontend/src/scripts/constants.js`

## Next Steps

1. **Backend Cleanup**
   ```bash
   cd backend
   rm auth.py database.py models.py schemas.py __init__.py
   mv test_auth.py tests/
   mv direct_test_run.py scripts/
   mv manual_test_run.py scripts/
   mv run_*.py scripts/
   mv save_test_results.py scripts/
   mv test_runner*.py scripts/
   ```

2. **Update HTML Files**
   - Update any script references to use new paths
   - Update CSS references to point to `../styles/`

3. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

4. **Run Tests**
   ```bash
   cd backend
   pytest
   ```

5. **Start Development**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source .venv/bin/activate
   python app/main.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Best Practices

- Keep related files together
- Use consistent naming conventions
- Document your architecture
- Maintain test coverage
- Use meaningful commit messages
- Keep .env files out of version control
- Use .env.example templates
- Document deployment procedures
