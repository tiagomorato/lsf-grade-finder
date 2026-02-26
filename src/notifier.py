import logging

import requests

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def format_new_grade_message(grade: dict) -> str:
    """Format a single grade into a Telegram notification message."""
    return (
        f"📝 New grade posted!\n\n"
        f"📚 Subject: {grade['name']}\n"
        f"🎯 Grade: {grade['grade']}\n"
        f"💎 Credits: {grade['credits']}"
    )


def _send_message(token: str, chat_id: str, text: str) -> None:
    """Send a message via Telegram Bot API."""
    url = TELEGRAM_API_URL.format(token=token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    logger.info("Telegram message sent successfully")


def notify_new_grades(token: str, chat_id: str, grades: list[dict]) -> None:
    """Send a Telegram notification for each new grade."""
    for grade in grades:
        message = format_new_grade_message(grade)
        _send_message(token, chat_id, message)


def notify_error(token: str, chat_id: str, error: Exception) -> None:
    """Send an error notification via Telegram."""
    message = f"⚠️ LSF Grade Finder Error\n\n{type(error).__name__}: {error}"
    try:
        _send_message(token, chat_id, message)
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")
