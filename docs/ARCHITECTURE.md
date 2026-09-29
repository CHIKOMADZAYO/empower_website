# Empower Automation — Architecture Decisions

## 1. Purpose

`automation.py` is the single deterministic entry point for every repetitive
lifecycle task: setup, quality, tests, DB, Docker, security, build, release,
deploy, health, cleanup. It wraps (never replaces) ruff, mypy, pytest,
Alembic, Compose, pip-audit/bandit, git, uvicorn — adding uniform logging,
secret redaction, exit codes, dry-run, idempotency, destructive guards, and a
pipeline that stops on first critical failure.

## 2. Layout (Clean Architecture, pragmatic)

```text
automation.py                  # tiny shim: sys.path + main()
automation/
  __main__.py                  # python -m automation
  cli/app.py                   # composition root: argparse + context + exit codes
  commands/                    # thin adapters (register + run per command)
  services/                    # business logic: env, python, quality, test,
                               # db, docker, security, ops
  infrastructure/context.py    # AppContext, AutomationError, Step/PipelineResult
  config/settings.py           # Settings dataclass, REQUIRED_VARS, dotenv loader
  utils/                       # secret-safe logging, output, process runner
```

Dependency rule: commands -> services -> infrastructure/config/utils.
Services never import argparse; commands never run subprocesses directly.


## 3. Decisions & rationale

- **argparse, no click/typer**: zero new deps, explicit per-command help.
- **AppContext injection**: ctx (settings, dry_run, force, verbose, logger)
  passed to every command/service instead of globals (DI, testable).
- **Frozen Settings dataclass**: one source for paths + env defaults; dotenv
  loader never overrides real env (DRY, single source of truth).
- **AutomationError + exit codes**: expected failure -> msg + hint, exit 1;
  usage -> exit 2; Ctrl-C -> 130. `build` stops at first raise (fail-fast).
- **Secret-safe logging**: filter redacts SECRET/PASSWORD/TOKEN/API_KEY/
  DATABASE_URL/Bearer values; scanners report paths + rules, never values.
- **--dry-run everywhere**: mutating services log the exact command first.
- **Destructive guards**: downgrade/reset prompt [y/N]; --force skips; reset
  refuses ENVIRONMENT=production without --force.
- **Idempotent setup**: venv reuse, safe reinstall, .env never overwritten,
  create_all/seed skip when data exists.
- **Alembic + create_all fallback**: real migrations in backend/alembic with
  0001_initial; `db upgrade` falls back to init_db() when alembic missing.
- **Pytest markers**: `integration` splits unit vs integration; -k slice for
  API; automation self-tests join unit/all runs.
- **Optional scanners**: pip-audit/bandit warn-skip when absent; secret scan,
  env validation, Dockerfile sanity always run.
- **Compose profiles**: queue (RabbitMQ) + frontend stay opt-in; default up
  is api + postgres + redis.
- **CI != CD**: ci.yml builds/tests/scans (no push); cd.yml is tag-triggered,
  pushes GHCR, then health-gates.

## 4. Flows

- `build`: format? -> lint -> typecheck -> unit -> integration -> security
  -> package -> docker. First failure raises, exit non-zero.
- `deploy --env production`: strict env validate -> docker build ->
  compose up -> GET /health -> ok or rollback hint.
- `db reset --force`: prod guard -> confirm -> downgrade base (best effort)
  -> drop_all/create_all -> seed.

## 5. Test strategy

- backend/tests/test_auth.py -> unit (signup/login/401/409 paths).
- backend/tests/test_db.py -> schema exists + seed idempotency.
- backend/tests/test_endpoints.py -> @pytest.mark.integration, TestClient.
- automation/tests/test_automation.py -> CLI parsing, env validation,
  dry-run clean/health (no network/docker).

## 6. Security model

Never committed: .env, *.db, dist/, venvs (.gitignore + .dockerignore).
Prod gates: SECRET_KEY >= 32 chars, no SQLite DATABASE_URL, USER appuser in
Dockerfile, GHCR via GITHUB_TOKEN, app secrets only via GitHub Secrets.

## 7. Deliberately NOT built

No plugin framework/YAML engine, no ORM inside automation, no fake queue
worker (RabbitMQ ships as a profile for later), no K8s manifests.

## 8. Extending

New command: automation/commands/<name>.py with register + run, wire into
cli/app.py (register + _HANDLERS), add tests in automation/tests/.
New check: function in the matching service, called from the command and
from build/check as appropriate.
