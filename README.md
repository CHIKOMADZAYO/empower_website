# Empower

Empower is a community-focused web platform for showcasing projects, stories,
and opportunities. FastAPI backend, Vite frontend, PostgreSQL in production
(SQLite for local dev), Redis/RabbitMQ via Compose profiles.

## Project structure

```text
empower/
├── automation.py            # Central automation CLI (start here)
├── automation/              # CLI: cli/ commands/ services/ config/ utils/
├── backend/                 # FastAPI app (app/), tests/, scripts/, alembic/
├── frontend/                # Vite frontend app
├── docs/                    # API / architecture / setup / deployment
├── .github/workflows/       # ci.yml (quality+tests+docker) / cd.yml (release)
├── Dockerfile               # Backend image (non-root, healthcheck)
├── frontend/Dockerfile      # Frontend dev/build/nginx stages
├── docker-compose.yml       # api + postgres + redis (+queue/frontend profiles)
├── alembic.ini              # DB migrations config
├── pyproject.toml           # Deps, ruff, mypy, pytest, bandit config
├── .env.example             # Root env template (copy to .env, never commit)
└── ARCHITECTURE.md          # Automation + system design decisions
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the app data flow.

## Tech stack

- Backend: Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic
- Quality/tests: Ruff, mypy, pytest (+ coverage)
- Data: PostgreSQL (prod) / SQLite (dev), Redis, RabbitMQ (opt-in profile)
- Ops: Docker + Compose, GitHub Actions (CI separate from CD)

## Prerequisites

- Python 3.12+
- Node.js 18+ / npm (frontend only)
- Docker + Docker Compose (containers only)
- Git


## Backend setup (recommended: automation CLI)

```bash
python automation.py setup            # venv, deps, .env, validate, migrate, tests
python automation.py setup --seed     # ...plus demo data
python automation.py setup --dry-run  # preview only
```

Manual equivalent:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python automation.py db upgrade
python automation.py db seed
```

The app entry point is [backend/app/main.py](backend/app/main.py)
(`GET /api/v1/health`).

## Configuration

```bash
cp .env.example .env            # root (compose, automation, deploy)
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env   # optional
```

Required variables (validated by `setup`, `security --strict`, `deploy`):

| Variable | Used by | Notes |
|---|---|---|
| `DATABASE_URL` | backend, Alembic, compose | SQLite dev-only; Postgres in prod |
| `SECRET_KEY` / `EMPOWER_SECRET_KEY` | backend JWT, compose | >= 32 random chars in prod |
| `ENVIRONMENT` | automation gates | development / staging / production |
| `REDIS_URL` | cache/rate-limit | optional locally |

Generate a secret: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
Never commit `.env`. GitHub Actions Secrets hold prod values (see CI/CD).

## CLI reference (all commands support `--help`, `--verbose`, `--dry-run`)

```bash
python automation.py setup [--no-venv] [--no-install] [--no-migrate] [--no-test] [--seed] [--check-services]
python automation.py format [--check]      # ruff format (backend + automation)
python automation.py lint                  # ruff check
python automation.py typecheck             # mypy backend/app
python automation.py check                 # pre-commit: git + format? + lint + types + unit
python automation.py test [--unit | --integration | --api] [--coverage]
python automation.py db migrate -m "msg"   # new Alembic revision
python automation.py db upgrade [rev]      # default: head (create_all fallback if no alembic)
python automation.py db downgrade [rev]    # confirm required (default: -1)
python automation.py db seed               # idempotent demo data
python automation.py db reset [--force]    # confirm required; refuses prod w/o --force
python automation.py docker build [--service X]
python automation.py docker up|down|restart [--service X]
python automation.py docker logs [--service X] [-f]
python automation.py docker ps
python automation.py docker migrate [--service backend]
python automation.py security [--strict]   # pip-audit + secrets + env + bandit + Dockerfile
python automation.py build [--skip-integration] [--skip-docker]
python automation.py clean [--include-db]
python automation.py release --bump patch|minor|major [--push]
python automation.py deploy --env staging|production [--health-url ...] [--skip-build]
python automation.py health [--url ...] [--timeout 10]
```

Exit codes: `0` ok · `1` task failure (build stops at first failure) ·
`2` usage error · `130` interrupted.

## Testing

```bash
python automation.py test                  # backend all + automation self-tests
python automation.py test --unit           # -m "not integration"
python automation.py test --integration    # -m integration (TestClient + SQLite)
python automation.py test --api            # endpoint/auth/contact/project/story slice
python automation.py test --unit --coverage
```

`backend/tests/test_db.py` covers schema + seed idempotency;
`test_endpoints.py` is `@pytest.mark.integration`. Build fails if tests fail.

## Code quality

```bash
python automation.py format --check && python automation.py lint && python automation.py typecheck
# or: python automation.py check
```

Production build (`build`) fails on any quality gate.

## Database

The configured Alembic history lives in `backend/migrations/versions`
(`backend/alembic.ini` points there). Destructive commands need confirmation unless
`--force`. Never run `db reset` against production data.

## Docker

```bash
docker compose up --build                  # api + postgres + redis
docker compose --profile queue up --build  # ...plus RabbitMQ
docker compose --profile frontend up       # ...plus Vite dev
python automation.py docker migrate        # alembic upgrade head in container
```

Images run as non-root `appuser` with `/api/v1/health` healthchecks.

## CI/CD

- **CI** (`.github/workflows/ci.yml`): checkout → Python 3.12/3.13 →
  format?/lint/typecheck → DB migrate+seed → unit+integration → frontend
  build → security → Docker build (no push). Trigger: push/PR + manual.
- **CD** (`.github/workflows/cd.yml`): tag `v*.*.*` (or manual) → strict
  security → GHCR push → deploy placeholder → `health` gate.
- **Secrets**: repo Settings → Secrets and variables → Actions:
  `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`, `POSTGRES_PASSWORD`,
  `RABBITMQ_PASSWORD`, `HEALTH_URL`, deploy credentials. Never `echo` them;
  automation logs redact secret values automatically.

## Deployment

Push tag → CI → security → image → deploy → health check → success/rollback:

```bash
python automation.py release --bump minor --push   # or: git tag v1.1.0 && git push --tags
# CD builds ghcr.io/<org>/<repo>:v1.1.0, deploys, then:
python automation.py health --url https://<host>/api/v1/health
```

Unhealthy deploy → `docker compose down` + redeploy previous image
(the `deploy` command prints this hint automatically).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ruff/mypy/alembic not installed` | `python automation.py setup` (installs `backend/requirements.txt`) |
| Migration `No support for ALTER of constraints (SQLite)` | Keep constraints inline in `create_table` (see `0001_initial`); SQLite can't ALTER-add them |
| JWT `InsecureKeyLengthWarning` in tests | Dev-only short key; set a 32+ char `SECRET_KEY` in `.env` |
| DB locked / stale dev data | `python automation.py db reset --force` (dev only) |
| Compose can't reach Postgres | `python automation.py setup --check-services`; check `.env` + `docker compose ps` |
| Need full trace | Append `--verbose` (DEBUG logs, tracebacks for unexpected errors) |

## Security considerations

- No secrets in code/logs/images: `.env` gitignored, logger redacts values,
  scanners report file+rule only, Dockerfile has no `ARG/ENV SECRET`.
- Weak-key and SQLite-in-prod gates block `security --strict` / prod `deploy`.
- Containers run as `USER appuser`; Compose secrets come from environment.

## Documentation

- [docs/API.md](docs/API.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) ·
  [docs/SETUP.md](docs/SETUP.md) · [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) ·
  [ARCHITECTURE.md](ARCHITECTURE.md) (automation design) ·
  [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
