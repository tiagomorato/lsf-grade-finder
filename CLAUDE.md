# CLAUDE.md

## Project Overview

LSF Grade Finder — automated grade checker for Uni Hildesheim's LSF portal. Scrapes grades via `requests` + `BeautifulSoup4` and sends Telegram notifications when new grades appear.

## Tech Stack

- Python 3.10+
- `requests` + `beautifulsoup4` for scraping (no Selenium/browser)
- `python-dotenv` for config
- Telegram Bot API (direct HTTP, no wrapper library)
- JSON file for grade persistence (`data/grades.json`)

## Package Manager

**Use `uv` for all package management.** Never use `pip` directly.

```bash
uv sync --all-extras    # Install all deps including dev
uv run <command>        # Run anything in the venv
```

## Project Structure

```
src/
  config.py    — Load/validate env vars
  scraper.py   — Login + grade parsing (requests + BS4)
  storage.py   — JSON grade persistence + diff detection
  notifier.py  — Telegram notifications
  main.py      — Entry point (once/loop modes)
tests/
  conftest.py  — Shared HTML fixtures and mock data
  unit/        — Fast tests, no network, mocked deps
  e2e/         — Full scrape flow against mocked HTTP (uses `responses` library)
data/          — Runtime grade storage (grades.json, gitignored)
```

## Common Commands

```bash
uv run ruff check .              # Lint
uv run ruff format --check .     # Check formatting
uv run ruff format .             # Auto-format
uv run pytest tests/unit/ -v     # Unit tests only
uv run pytest tests/e2e/ -v      # E2E tests only
uv run pytest tests/ -v          # All tests
uv run python -m src.main        # Run the grade checker (needs .env)
```

## Lint & Formatting

- Ruff for both linting and formatting (configured in `pyproject.toml`)
- Rules: E, F, I, W
- Line length: 88
- Always run `uv run ruff check .` and `uv run ruff format --check .` before committing

## Testing

- Unit tests mock all I/O — no network calls, use `tmp_path` for file tests
- E2E tests use the `responses` library to mock the full HTTP flow (LSF login + grades + Telegram API)
- Fixtures in `tests/conftest.py`: sample login HTML, grade table HTML, mock grade dicts

## Configuration

All config via environment variables (loaded from `.env` by `python-dotenv`). See `.env.example` for the full list. Required: `LSF_BASE_URL`, `LSF_USERNAME`, `LSF_PASSWORD`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Key Design Decisions

- **No Selenium** — LSF is server-rendered HTML, `requests` + BS4 is sufficient and avoids the ~400MB Chrome dependency
- **Auto-detect login form fields** — finds `<input type="text">` and `<input type="password">` rather than hardcoding field names
- **Grade diff uses `(name, grade)` composite key** — a changed grade for the same subject counts as new
- **Two run modes**: `once` (for GitHub Actions cron) and `loop` (for Docker with `time.sleep`)
