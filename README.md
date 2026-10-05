# LSF Grade Finder

[![CI](https://github.com/tiagomorato/lsf-grade-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/tiagomorato/lsf-grade-finder/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/tests-43%20passing-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Checks the Universität Hildesheim LSF portal for newly posted grades and sends a Telegram message the moment one appears, instead of logging in by hand several times a day during exam season.

> Part of a small suite of automations for university portals, alongside [learnweb-content-finder](https://github.com/tiagomorato/learnweb-content-finder) (course material changes) and [uni-mail-finder](https://github.com/tiagomorato/uni-mail-finder) (university email).

## How it works

```
login (JSF form) ──▶ portal page ──▶ Notenspiegel link ──▶ grade table
                                                              │
        Telegram ◀── new grades only ◀── diff against data/grades.json
```

1. **Login.** LSF is a JSF application. The scraper reads the login form, carries over the hidden fields (`ViewState`, CSRF token), detects the username and password inputs by type rather than by their generated names, and follows `<meta http-equiv="refresh">` redirects.
2. **Find the grades.** The Notenspiegel URL contains a session-specific token, so it is never hardcoded. The scraper locates the link on the portal page after login.
3. **Parse.** The grade table is parsed with BeautifulSoup into `{name, grade, credits}` records.
4. **Diff and notify.** Records are compared against the last known state in `data/grades.json`. Only new grades trigger a notification, and the state is saved afterwards.

Network calls retry with exponential backoff, and any failure is reported to the same Telegram chat so a broken login never fails silently. Session URLs are deliberately kept out of the logs.

No browser is involved. `requests` and `BeautifulSoup4` are enough, which keeps a run under 20 seconds.

## Testing

43 tests, run on every push by [GitHub Actions](.github/workflows/ci.yml) together with `ruff` lint and format checks.

| Suite | What it covers |
|---|---|
| `tests/unit/` | Login form parsing, meta-refresh handling, grade-table parsing, diffing, storage, config validation and message formatting |
| `tests/e2e/` | The full login → Notenspiegel → parse → notify flow against HTTP responses mocked with [`responses`](https://github.com/getsentry/responses), so no real portal is needed |

```bash
uv sync --all-extras
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

## Running it

You need a Telegram bot token (from [@BotFather](https://t.me/BotFather)) and your chat ID (from [@userinfobot](https://t.me/userinfobot)).

### Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `LSF_BASE_URL` | Yes | — | LSF login page, e.g. `https://lsf.uni-hildesheim.de/` |
| `LSF_USERNAME` | Yes | — | LSF username |
| `LSF_PASSWORD` | Yes | — | LSF password |
| `TELEGRAM_BOT_TOKEN` | Yes | — | Bot token |
| `TELEGRAM_CHAT_ID` | Yes | — | Chat that receives notifications |
| `RUN_MODE` | No | `once` | `once` for cron or Actions, `loop` for Docker |
| `CHECK_INTERVAL_MINUTES` | No | `30` | Minutes between checks in loop mode |

### Locally or on a server

```bash
cp .env.example .env              # fill in your credentials
uv run python -m src.main         # one check
uv run python -m src.main --grades  # send a table of all known grades with average and credit total
docker compose up -d              # or run continuously in loop mode
```

### Scheduled with GitHub Actions

Run the schedule from a **private** repository so that the run logs and the cached `grades.json` stay private, and let it check out this code:

```yaml
# .github/workflows/check-grades.yml in your private repo
on:
  schedule:
    - cron: "0 */4 * * *"
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          repository: tiagomorato/lsf-grade-finder
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - uses: actions/cache/restore@v4
        with:
          path: data/grades.json
          key: grades-data
      - run: uv run python -m src.main
        env:
          LSF_BASE_URL: ${{ secrets.LSF_BASE_URL }}
          LSF_USERNAME: ${{ secrets.LSF_USERNAME }}
          LSF_PASSWORD: ${{ secrets.LSF_PASSWORD }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      - uses: actions/cache/save@v4
        if: always()
        with:
          path: data/grades.json
          key: grades-data-${{ github.run_id }}
```

The first run has no stored state, so it reports every current grade once. After that, only new grades are sent.

## Disclaimer

An unofficial personal tool, not affiliated with Universität Hildesheim. It only reads your own grades with your own credentials, at a low request rate.

## License

[MIT](LICENSE)
