# Setup Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- Git

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv .venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Initialize Database

```bash
python scripts/seed_db.py
```

### 6. Run Tests

```bash
pytest
```

### 7. Start Server

```bash
python app/main.py
```

Server will run on `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed
```

### 3. Start Development Server

```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Development Workflow

1. Start backend server:
   ```bash
   cd backend
   source .venv/bin/activate
   python app/main.py
   ```

2. In another terminal, start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Access application at `http://localhost:3000`

## Running Tests

### Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest tests/test_auth.py # Run specific test
pytest -v                 # Verbose output
pytest --cov             # With coverage
```

### Frontend Tests

```bash
cd frontend
npm run test  # If configured
```

## Troubleshooting

### Python: "No module named 'fastapi'"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Node: "npm: command not found"
- Install Node.js from https://nodejs.org/

### Port already in use
- Backend: Change port in `.env` (default 8000)
- Frontend: Change port in `vite.config.js` (default 3000)

### Database locked
- Delete `backend/data/empower.db` and reinitialize
- Run: `python scripts/seed_db.py`

## Database Management

### Reset Database

```bash
cd backend
rm data/empower.db
python scripts/seed_db.py
```

### Seed Sample Data

```bash
cd backend
python scripts/seed_db.py
```

## Next Steps

- Review [API Documentation](API.md)
- Check [Architecture](ARCHITECTURE.md)
- See [Deployment Guide](DEPLOYMENT.md)
