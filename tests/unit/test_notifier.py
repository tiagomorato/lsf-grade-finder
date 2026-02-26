import responses

from src.notifier import format_new_grade_message, notify_error, notify_new_grades


class TestFormatMessage:
    def test_contains_all_fields(self):
        grade = {"name": "Datenbanken", "grade": "2,0", "credits": "9,0"}
        msg = format_new_grade_message(grade)
        assert "Datenbanken" in msg
        assert "2,0" in msg
        assert "9,0" in msg

    def test_format_structure(self):
        grade = {"name": "Test Subject", "grade": "1,0", "credits": "6,0"}
        msg = format_new_grade_message(grade)
        assert "Subject: Test Subject" in msg
        assert "Grade: 1,0" in msg
        assert "Credits: 6,0" in msg


class TestNotifyNewGrades:
    @responses.activate
    def test_sends_one_message_per_grade(self):
        responses.add(
            responses.POST,
            "https://api.telegram.org/bot123:ABC/sendMessage",
            json={"ok": True},
            status=200,
        )

        grades = [
            {"name": "Subject A", "grade": "1,0", "credits": "6,0"},
            {"name": "Subject B", "grade": "2,0", "credits": "9,0"},
        ]
        notify_new_grades("123:ABC", "456", grades)

        assert len(responses.calls) == 2

    @responses.activate
    def test_sends_correct_payload(self):
        responses.add(
            responses.POST,
            "https://api.telegram.org/bot123:ABC/sendMessage",
            json={"ok": True},
            status=200,
        )

        grades = [{"name": "Datenbanken", "grade": "2,0", "credits": "9,0"}]
        notify_new_grades("123:ABC", "456", grades)

        assert len(responses.calls) == 1
        body = responses.calls[0].request.body
        assert "456" in body.decode() if isinstance(body, bytes) else body
        assert "Datenbanken" in body.decode() if isinstance(body, bytes) else body


class TestNotifyError:
    @responses.activate
    def test_sends_error_message(self):
        responses.add(
            responses.POST,
            "https://api.telegram.org/botTOKEN/sendMessage",
            json={"ok": True},
            status=200,
        )

        notify_error("TOKEN", "789", RuntimeError("test error"))

        assert len(responses.calls) == 1
        body = responses.calls[0].request.body
        decoded = body.decode() if isinstance(body, bytes) else body
        assert "test error" in decoded

    @responses.activate
    def test_error_notification_failure_does_not_raise(self):
        responses.add(
            responses.POST,
            "https://api.telegram.org/botTOKEN/sendMessage",
            json={"ok": False},
            status=500,
        )

        # Should not raise even if Telegram API fails
        notify_error("TOKEN", "789", RuntimeError("test error"))
