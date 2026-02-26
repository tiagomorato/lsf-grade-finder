import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GRADES_FILE = DATA_DIR / "grades.json"


def load_known_grades() -> list[dict]:
    """Load previously saved grades from JSON file."""
    if not GRADES_FILE.exists():
        return []

    try:
        data = json.loads(GRADES_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Could not read grades file: {e}")
        return []


def save_grades(grades: list[dict]) -> None:
    """Save grades to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    GRADES_FILE.write_text(
        json.dumps(grades, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info(f"Saved {len(grades)} grades to {GRADES_FILE}")


def find_new_grades(current: list[dict], known: list[dict]) -> list[dict]:
    """Find grades in current that are not in known.

    Uses (name, grade) as composite key — a changed grade for the same
    subject counts as a new entry.
    """
    known_keys = {(g["name"], g["grade"]) for g in known}
    return [g for g in current if (g["name"], g["grade"]) not in known_keys]
