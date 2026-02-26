# LSF Grade Finder

Automated grade checker for Uni Hildesheim's LSF portal. Checks for new grades periodically and sends Telegram notifications when new grades are posted.

## Features

- Lightweight scraper using `requests` + `BeautifulSoup4` (no browser needed)
- Telegram notifications for new grades
- Two deployment options: GitHub Actions (free, zero maintenance) or Docker
- JSON-based grade persistence for change detection

## Quick Start (GitHub Actions)

This is the easiest setup — no server required, completely free.

### 1. Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts to create your bot
3. Copy the **bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID

1. Search for **@userinfobot** on Telegram and start a chat
2. It will reply with your **chat ID** (a number like `123456789`)

### 3. Fork & Configure

1. **Fork** this repository on GitHub
2. Go to your fork's **Settings → Secrets and variables → Actions**
3. Add these **Repository secrets**:

   | Secret | Value |
   |---|---|
   | `LSF_BASE_URL` | `https://lsf.uni-hildesheim.de/` |
   | `LSF_GRADES_URL` | Your LSF grades page URL (see `.env.example`) |
   | `LSF_USERNAME` | Your LSF username |
   | `LSF_PASSWORD` | Your LSF password |
   | `TELEGRAM_BOT_TOKEN` | Bot token from step 1 |
   | `TELEGRAM_CHAT_ID` | Chat ID from step 2 |

4. Go to **Actions** tab and enable workflows
5. The grade checker will now run every 30 minutes automatically

You can also trigger a manual check: **Actions → Check Grades → Run workflow**.

## Alternative: Docker Deployment

For running on your own server or locally:

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/lsf-grade-finder.git
cd lsf-grade-finder

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
docker compose up -d
```

The container runs in loop mode, checking every 30 minutes by default. Grade data is persisted in `./data/grades.json`.

## Local Development

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Run once
uv run python -m src.main

# Run tests
uv run pytest tests/ -v

# Lint
uv run ruff check .
uv run ruff format --check .
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `LSF_BASE_URL` | Yes | — | LSF login page URL |
| `LSF_GRADES_URL` | Yes | — | Direct URL to grade overview |
| `LSF_USERNAME` | Yes | — | LSF username |
| `LSF_PASSWORD` | Yes | — | LSF password |
| `TELEGRAM_BOT_TOKEN` | Yes | — | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | — | Your Telegram chat ID |
| `RUN_MODE` | No | `once` | `once` (cron/Actions) or `loop` (Docker) |
| `CHECK_INTERVAL_MINUTES` | No | `30` | Minutes between checks in loop mode |
