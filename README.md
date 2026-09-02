# Empower

A full-stack web application for empowering communities through projects and storytelling.

## Project Structure

```
empower/
├── backend/          # FastAPI backend service
├── frontend/         # HTML/CSS frontend
├── docs/            # Project documentation
└── .github/         # GitHub workflows (CI/CD)
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m pytest  # Run tests
python app/main.py  # Start server
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev  # Start development server
npm run build  # Build for production
```

## Requirements

- **Backend**: Python 3.8+, FastAPI
- **Frontend**: Node.js 14+, npm

## Documentation

See [docs/](docs/) for detailed documentation:
- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)
- [Deployment](docs/DEPLOYMENT.md)

## Development

### Running Tests

```bash
cd backend
pytest  # Run all tests
pytest tests/test_auth.py  # Run specific test
```

### Database

- Development database: `backend/data/empower.db`
- See `backend/scripts/` for database utilities

## License

See LICENSE file for details.
