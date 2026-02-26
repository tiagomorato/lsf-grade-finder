import logging
import time

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 2


def _retry(func, *args, **kwargs):
    """Retry a function with exponential backoff."""
    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            wait = BACKOFF_BASE**attempt
            logger.warning(
                f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}. "
                f"Retrying in {wait}s..."
            )
            time.sleep(wait)
    raise last_exception


def _extract_login_fields(html: str) -> tuple[dict, str]:
    """Extract hidden form fields and detect username/password input names.

    Returns (form_data, form_action) where form_data contains all hidden
    fields plus the detected username and password field names mapped to
    empty strings.
    """
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise ValueError("No login form found on page")

    action = form.get("action", "")

    form_data = {}
    for inp in form.find_all("input"):
        input_type = (inp.get("type") or "").lower()
        name = inp.get("name")
        if not name:
            continue
        if input_type == "hidden":
            form_data[name] = inp.get("value", "")

    username_field = None
    password_field = None

    for inp in form.find_all("input"):
        input_type = (inp.get("type") or "").lower()
        name = inp.get("name")
        if not name:
            continue
        if input_type == "text" and username_field is None:
            username_field = name
        elif input_type == "password" and password_field is None:
            password_field = name

    if not username_field or not password_field:
        raise ValueError("Could not detect username/password fields in login form")

    submit_button = form.find("input", {"type": "submit"})
    if submit_button and submit_button.get("name"):
        form_data[submit_button["name"]] = submit_button.get("value", "")

    return form_data, action, username_field, password_field


def _follow_meta_refresh(
    session: requests.Session, url: str, html: str
) -> tuple[str, str]:
    """Follow a meta http-equiv refresh redirect if present.

    Returns (final_url, final_html).
    """
    from urllib.parse import urljoin

    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"http-equiv": "refresh"})
    if meta:
        content = meta.get("content", "")
        # Format: "0; URL=/some/path"
        parts = content.split("URL=", 1)
        if len(parts) == 2:
            redirect_url = urljoin(url, parts[1].strip())
            logger.info(f"Following meta refresh to {redirect_url}")
            resp = session.get(redirect_url)
            resp.raise_for_status()
            return resp.url, resp.text
    return url, html


def login(
    session: requests.Session,
    base_url: str,
    username: str,
    password: str,
) -> str:
    """Log into LSF and return the post-login page HTML."""
    logger.info("Fetching login page...")
    resp = session.get(base_url)
    resp.raise_for_status()

    current_url, html = _follow_meta_refresh(session, resp.url, resp.text)

    form_data, action, user_field, pass_field = _extract_login_fields(html)

    form_data[user_field] = username
    form_data[pass_field] = password

    if action and not action.startswith("http"):
        from urllib.parse import urljoin

        action = urljoin(current_url, action)
    post_url = action or base_url

    logger.info("Submitting login form...")
    resp = session.post(post_url, data=form_data)
    resp.raise_for_status()

    if "login" in resp.url.lower() and "error" in resp.text.lower():
        raise RuntimeError("Login failed — check your credentials")

    logger.info("Login successful.")
    return resp.text


def fetch_grades(session: requests.Session, portal_html: str) -> list[dict]:
    """Find the Notenspiegel link on the portal page and parse grades."""
    soup = BeautifulSoup(portal_html, "html.parser")

    link = soup.find("a", string=lambda t: t and "Notenspiegel" in t)
    if not link or not link.get("href"):
        raise ValueError("Could not find Notenspiegel link on portal page")

    grades_url = link["href"]
    logger.info(f"Following Notenspiegel link: {grades_url}")
    resp = session.get(grades_url)
    resp.raise_for_status()

    return _parse_grade_table(BeautifulSoup(resp.text, "html.parser"))


def _parse_grade_table(soup: BeautifulSoup) -> list[dict]:
    """Parse the grade table from a Notenspiegel page."""
    table = soup.find("table")
    if not table:
        logger.warning("No grade table found on page")
        return []

    grades = []
    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue

        cell_texts = [cell.get_text(strip=False) for cell in cells]
        if len(cell_texts) < 5:
            continue

        raw_name = cell_texts[1] if len(cell_texts) > 1 else ""
        raw_grade = cell_texts[2] if len(cell_texts) > 2 else ""
        raw_credits = cell_texts[4] if len(cell_texts) > 4 else ""

        if "/\n" in raw_name:
            name = raw_name.split("/\n")[1].strip()
        elif "/" in raw_name:
            name = raw_name.split("/", 1)[1].strip()
        else:
            name = raw_name.strip()

        grade = raw_grade.strip()
        if not grade:
            continue

        credits = raw_credits.strip()

        grades.append({"name": name, "grade": grade, "credits": credits})

    logger.info(f"Parsed {len(grades)} grades from table")
    return grades


def scrape_grades(base_url: str, username: str, password: str) -> list[dict]:
    """Full scrape flow: login + find Notenspiegel + parse grades."""
    session = requests.Session()

    portal_html = _retry(login, session, base_url, username, password)
    grades = _retry(fetch_grades, session, portal_html)

    return grades
