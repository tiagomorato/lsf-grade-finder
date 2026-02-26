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


def format_grades_table(grades: list[dict]) -> str:
    """Format grades into a monospace summary table for Telegram."""
    lines = ["📊 Grade Summary\n"]
    lines.append("<pre>")
    lines.append(f"{'Course':<20} │ Grade │ Credits")
    lines.append("─" * 20 + "─┼───────┼────────")

    graded = []
    for g in [g for g in grades if not g["name"].startswith("Vorläufig")]:
        name = g["name"]
        if len(name) > 20:
            name = name[:17] + "..."
        grade_str = g["grade"].center(5)
        credits_str = g["credits"].rjust(5)
        lines.append(f"{name:<20} │ {grade_str} │ {credits_str}")

        try:
            grade_val = float(g["grade"].replace(",", "."))
            credits_val = float(g["credits"].replace(",", "."))
            graded.append((grade_val, credits_val))
        except ValueError:
            pass

    lines.append("─" * 20 + "─┼───────┼────────")

    if graded:
        avg = sum(v for v, _ in graded) / len(graded)
        avg_str = f"{avg:.1f}".replace(".", ",").center(5)
        total = sum(c for _, c in graded)
        total_str = f"{total:.1f}".replace(".", ",").rjust(5)
    else:
        avg_str = "  -  "
        total_str = "    -"

    lines.append(f"{'Average':<20} │ {avg_str} │ {total_str}")
    lines.append("</pre>")
    return "\n".join(lines)


def send_grades_summary(token: str, chat_id: str, grades: list[dict]) -> None:
    """Format and send a grade summary table via Telegram."""
    message = format_grades_table(grades)
    _send_message(token, chat_id, message)


def notify_error(token: str, chat_id: str, error: Exception) -> None:
    """Send an error notification via Telegram."""
    message = f"⚠️ LSF Grade Finder Error\n\n{type(error).__name__}: {error}"
    try:
        _send_message(token, chat_id, message)
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")
