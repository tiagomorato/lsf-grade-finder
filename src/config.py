import logging
import os
import sys

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

REQUIRED_VARS = [
    "LSF_BASE_URL",
    "LSF_USERNAME",
    "LSF_PASSWORD",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
]


def load_config() -> dict:
    """Load and validate configuration from environment variables."""
    load_dotenv()

    config = {}
    missing = []

    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        config[var.lower()] = value

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    config["run_mode"] = os.getenv("RUN_MODE", "once").lower()
    if config["run_mode"] not in ("once", "loop"):
        logger.error(f"RUN_MODE must be 'once' or 'loop', got '{config['run_mode']}'")
        sys.exit(1)

    try:
        config["check_interval_minutes"] = int(
            os.getenv("CHECK_INTERVAL_MINUTES", "30")
        )
    except ValueError:
        logger.error("CHECK_INTERVAL_MINUTES must be an integer")
        sys.exit(1)

    return config
