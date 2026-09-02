# Empower

Empower is a community-focused web platform for showcasing projects, stories, and opportunities. The project combines a FastAPI backend with a lightweight frontend built with Vite and static HTML/CSS/JavaScript.

## Project structure

```text
empower/
├── backend/          # FastAPI API and data layer
├── frontend/         # Vite frontend app
├── docs/             # Project documentation
├── .github/          # GitHub workflows
├── docker-compose.yml
├── LICENSE
├── README.md
└── PROJECT_STRUCTURE.md
```

## Tech stack

- Backend: Python, FastAPI, SQLAlchemy
- Frontend: Vite, HTML, CSS, JavaScript
- Database: SQLite for local development
- CI: GitHub Actions

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
python app/main.py
```

The app will start from the backend entry point defined in [backend/app/main.py](backend/app/main.py).

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

To build the production bundle:

```bash
cd frontend
npm run build
```

## Local development

### Run the backend

```bash
cd backend
python app/main.py
```

### Run the frontend

```bash
cd frontend
npm run dev
```

## Testing

```bash
cd backend
pytest
```

## Documentation

See the project docs for implementation and deployment details:

- [docs/API.md](docs/API.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/SETUP.md](docs/SETUP.md)
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
