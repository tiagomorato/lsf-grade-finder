import json

import responses

from src.main import check_grades
from tests.conftest import SAMPLE_GRADES_TABLE, SAMPLE_LOGIN_HTML

BASE_URL = "https://lsf.example.com/"
GRADES_URL = "https://lsf.example.com/grades"

CONFIG = {
    "lsf_base_url": BASE_URL,
    "lsf_grades_url": GRADES_URL,
    "lsf_username": "testuser",
    "lsf_password": "testpass",
    "telegram_bot_token": "123:ABC",
    "telegram_chat_id": "456",
    "run_mode": "once",
    "check_interval_minutes": 30,
}


def _setup_lsf_mocks():
    """Register mock responses for the full LSF flow."""
    # GET login page
    responses.add(
        responses.GET,
        BASE_URL,
        body=SAMPLE_LOGIN_HTML,
        status=200,
    )

    # POST login form
    responses.add(
        responses.POST,
        BASE_URL + "qisserver/rds?state=user&type=1",
        body="<html><body>Welcome</body></html>",
        status=200,
    )

    # GET grades page (returns table directly, no Notenspiegel link)
    responses.add(
        responses.GET,
        GRADES_URL,
        body=SAMPLE_GRADES_TABLE,
        status=200,
    )


def _setup_telegram_mock():
    """Register mock response for Telegram API."""
    responses.add(
        responses.POST,
        "https://api.telegram.org/bot123:ABC/sendMessage",
        json={"ok": True},
        status=200,
    )


class TestFullScrapeFlow:
    @responses.activate
    def test_first_run_detects_all_grades_as_new(self, tmp_path, monkeypatch):
        _setup_lsf_mocks()
        _setup_telegram_mock()

        # Use temp directory for grade storage
        monkeypatch.setattr("src.storage.DATA_DIR", tmp_path)
        monkeypatch.setattr("src.storage.GRADES_FILE", tmp_path / "grades.json")
        monkeypatch.setattr("src.main.load_known_grades", lambda: [])
        monkeypatch.setattr(
            "src.main.save_grades",
            lambda grades: (tmp_path / "grades.json").write_text(
                json.dumps(grades, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            ),
        )

        check_grades(CONFIG)

        # Should have sent 2 Telegram messages (2 grades with actual grades)
        telegram_calls = [c for c in responses.calls if "telegram" in c.request.url]
        assert len(telegram_calls) == 2

        # Grades should be saved
        saved = json.loads((tmp_path / "grades.json").read_text(encoding="utf-8"))
        assert len(saved) == 2
        assert saved[0]["name"] == "Einführung in die Informatik"
        assert saved[1]["name"] == "Datenbanken"

    @responses.activate
    def test_second_run_no_new_grades(self, tmp_path, monkeypatch):
        _setup_lsf_mocks()
        _setup_telegram_mock()

        existing_grades = [
            {"name": "Einführung in die Informatik", "grade": "1,3", "credits": "6,0"},
            {"name": "Datenbanken", "grade": "2,0", "credits": "9,0"},
        ]

        monkeypatch.setattr("src.storage.DATA_DIR", tmp_path)
        monkeypatch.setattr("src.storage.GRADES_FILE", tmp_path / "grades.json")
        monkeypatch.setattr("src.main.load_known_grades", lambda: existing_grades)
        monkeypatch.setattr("src.main.save_grades", lambda grades: None)

        check_grades(CONFIG)

        # No Telegram messages should be sent
        telegram_calls = [c for c in responses.calls if "telegram" in c.request.url]
        assert len(telegram_calls) == 0

    @responses.activate
    def test_new_grade_added(self, tmp_path, monkeypatch):
        """Simulate a new grade appearing that wasn't there before."""
        # Return a table with 3 grades (including one previously without a grade)
        grades_html = (
            "<html><body><table>"
            "<tr><th>Nr</th><th>Name</th><th>Note</th>"
            "<th>Status</th><th>LP</th></tr>"
            "<tr><td>1</td>"
            "<td>INF-001/\nEinführung in die Informatik</td>"
            "<td>1,3</td><td>bestanden</td><td>6,0</td></tr>"
            "<tr><td>2</td>"
            "<td>INF-002/\nDatenbanken</td>"
            "<td>2,0</td><td>bestanden</td><td>9,0</td></tr>"
            "<tr><td>3</td>"
            "<td>INF-003/\nSoftwaretechnik</td>"
            "<td>1,7</td><td>bestanden</td><td>6,0</td></tr>"
            "</table></body></html>"
        )

        responses.add(responses.GET, BASE_URL, body=SAMPLE_LOGIN_HTML, status=200)
        responses.add(
            responses.POST,
            BASE_URL + "qisserver/rds?state=user&type=1",
            body="<html><body>Welcome</body></html>",
            status=200,
        )
        responses.add(responses.GET, GRADES_URL, body=grades_html, status=200)
        _setup_telegram_mock()

        existing_grades = [
            {"name": "Einführung in die Informatik", "grade": "1,3", "credits": "6,0"},
            {"name": "Datenbanken", "grade": "2,0", "credits": "9,0"},
        ]

        saved_data = []

        def mock_save(grades):
            saved_data.extend(grades)

        monkeypatch.setattr("src.storage.DATA_DIR", tmp_path)
        monkeypatch.setattr("src.storage.GRADES_FILE", tmp_path / "grades.json")
        monkeypatch.setattr("src.main.load_known_grades", lambda: existing_grades)
        monkeypatch.setattr("src.main.save_grades", mock_save)

        check_grades(CONFIG)

        # Only 1 new grade → 1 Telegram message
        telegram_calls = [c for c in responses.calls if "telegram" in c.request.url]
        assert len(telegram_calls) == 1

        body = telegram_calls[0].request.body
        decoded = body.decode() if isinstance(body, bytes) else body
        assert "Softwaretechnik" in decoded

        # All 3 grades should be saved
        assert len(saved_data) == 3
