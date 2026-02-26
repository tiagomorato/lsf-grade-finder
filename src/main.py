import logging
import sys
import time

from src.config import load_config
from src.notifier import notify_error, notify_new_grades
from src.scraper import scrape_grades
from src.storage import find_new_grades, load_known_grades, save_grades

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def check_grades(config: dict) -> None:
    """Run a single grade check cycle."""
    logger.info("Starting grade check...")

    grades = scrape_grades(
        base_url=config["lsf_base_url"],
        grades_url=config["lsf_grades_url"],
        username=config["lsf_username"],
        password=config["lsf_password"],
    )

    known = load_known_grades()
    new_grades = find_new_grades(grades, known)

    if new_grades:
        logger.info(f"Found {len(new_grades)} new grade(s)!")
        notify_new_grades(
            config["telegram_bot_token"],
            config["telegram_chat_id"],
            new_grades,
        )
        save_grades(grades)
    else:
        logger.info("No new grades found.")
        if not known and grades:
            save_grades(grades)


def main() -> None:
    config = load_config()

    if config["run_mode"] == "once":
        try:
            check_grades(config)
        except Exception as e:
            logger.exception(f"Grade check failed: {e}")
            try:
                notify_error(
                    config["telegram_bot_token"],
                    config["telegram_chat_id"],
                    e,
                )
            except Exception:
                pass
            sys.exit(1)
    else:
        interval = config["check_interval_minutes"] * 60
        logger.info(
            f"Running in loop mode, checking every "
            f"{config['check_interval_minutes']} minutes"
        )
        while True:
            try:
                check_grades(config)
            except Exception as e:
                logger.exception(f"Grade check failed: {e}")
                try:
                    notify_error(
                        config["telegram_bot_token"],
                        config["telegram_chat_id"],
                        e,
                    )
                except Exception:
                    pass
            logger.info(f"Sleeping for {config['check_interval_minutes']} minutes...")
            time.sleep(interval)


if __name__ == "__main__":
    main()
