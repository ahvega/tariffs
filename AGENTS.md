# Repository Guidelines

## Project Structure & Module Organization
- Backend: `backend/sicargabox` (Django project). Key dirs: `api/`, `SicargaBox/`, `templates/`, `static/`, `tests/`, `theme/`.
- Frontends: `frontend/` and `mobile/` (not always required for backend work).
- Tools & scripts: `tools/` and top-level `src/` for auxiliary utilities.
- Config: `.env` (backend), `pytest.ini` (tests), Tailwind configs (`tailwind.config.js`, `postcss.config.js`).

## Build, Test, and Development Commands
- Setup Python env:
  - Windows PowerShell: `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
  - Install deps: `pip install -r backend/sicargabox/requirements.txt`
- Run Django locally: `python backend/sicargabox/manage.py migrate && python backend/sicargabox/manage.py runserver`
- Frontend CSS (Tailwind):
  - From `backend/sicargabox`: `npm install`
  - Dev watch: `npm run dev`
  - Production build: `npm run build`
- Tests (pytest + Django):
  - From `backend/sicargabox`: `pytest -v` (uses `DJANGO_SETTINGS_MODULE=test_settings`)
  - Coverage: `pytest --cov` (if coverage is configured)

## Coding Style & Naming Conventions
- Python: 4-space indent, type hints encouraged.
- Formatters/linters: `black`, `isort`, `flake8`, `mypy` (installed via requirements).
- Conventions: modules/files `snake_case.py`; classes `PascalCase`; functions/vars `snake_case`; constants `UPPER_SNAKE_CASE`.
- Run locally before committing: `black . && isort . && flake8 && mypy backend/sicargabox`

## Testing Guidelines
- Frameworks: `pytest`, `pytest-django`, optional `pytest-cov`.
- Location: tests live in `backend/sicargabox/tests/`.
- Naming: files `test_*.py`, tests use clear arrange–act–assert; prefer factory/setup helpers.
- Keep tests deterministic; use `test_settings.py` and avoid external services unless mocked.

## Commit & Pull Request Guidelines
- Commits: short, imperative summaries (e.g., "Fix tariff rounding in cotizador"). Body explains rationale and scope. Reference issues when relevant.
- PRs: include description, linked issue, test plan (commands, expected results), and screenshots for UI changes. Ensure `pytest` passes and code is formatted.

## Security & Configuration Tips
- Do not commit secrets; keep `.env` local. Minimum vars: Django `SECRET_KEY`, DB creds, and any Elasticsearch settings (see `ELASTICSEARCH_SETUP.md`).
- Use `test_settings.py` for tests; never point tests at production resources.

