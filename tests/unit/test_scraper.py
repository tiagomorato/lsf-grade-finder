import pytest
from bs4 import BeautifulSoup

from src.scraper import _extract_login_fields, _parse_grade_table
from tests.conftest import (
    SAMPLE_GRADES_TABLE,
    SAMPLE_GRADES_TABLE_EMPTY,
    SAMPLE_GRADES_TABLE_NO_TABLE,
    SAMPLE_LOGIN_HTML,
    SAMPLE_LOGIN_HTML_NO_FORM,
    SAMPLE_LOGIN_HTML_NO_PASSWORD,
)


class TestExtractLoginFields:
    def test_extracts_hidden_fields(self):
        form_data, action, user_field, pass_field = _extract_login_fields(
            SAMPLE_LOGIN_HTML
        )
        assert form_data["javax.faces.ViewState"] == "abc123viewstate"
        assert form_data["csrf_token"] == "xyz789csrf"

    def test_detects_username_field(self):
        _, _, user_field, _ = _extract_login_fields(SAMPLE_LOGIN_HTML)
        assert user_field == "asdf"

    def test_detects_password_field(self):
        _, _, _, pass_field = _extract_login_fields(SAMPLE_LOGIN_HTML)
        assert pass_field == "fdsauhi"

    def test_extracts_form_action(self):
        _, action, _, _ = _extract_login_fields(SAMPLE_LOGIN_HTML)
        assert "state=user" in action

    def test_extracts_submit_button(self):
        form_data, _, _, _ = _extract_login_fields(SAMPLE_LOGIN_HTML)
        assert "loginForm:login" in form_data

    def test_no_form_raises(self):
        with pytest.raises(ValueError, match="No login form found"):
            _extract_login_fields(SAMPLE_LOGIN_HTML_NO_FORM)

    def test_no_password_field_raises(self):
        with pytest.raises(ValueError, match="Could not detect"):
            _extract_login_fields(SAMPLE_LOGIN_HTML_NO_PASSWORD)


class TestParseGradeTable:
    def test_parses_grades(self):
        soup = BeautifulSoup(SAMPLE_GRADES_TABLE, "html.parser")
        grades = _parse_grade_table(soup)
        assert len(grades) == 2
        assert grades[0]["name"] == "Einführung in die Informatik"
        assert grades[0]["grade"] == "1,3"
        assert grades[0]["credits"] == "6,0"
        assert grades[1]["name"] == "Datenbanken"
        assert grades[1]["grade"] == "2,0"
        assert grades[1]["credits"] == "9,0"

    def test_skips_rows_without_grade(self):
        soup = BeautifulSoup(SAMPLE_GRADES_TABLE, "html.parser")
        grades = _parse_grade_table(soup)
        names = [g["name"] for g in grades]
        assert "Softwaretechnik" not in names

    def test_empty_table(self):
        soup = BeautifulSoup(SAMPLE_GRADES_TABLE_EMPTY, "html.parser")
        grades = _parse_grade_table(soup)
        assert grades == []

    def test_no_table(self):
        soup = BeautifulSoup(SAMPLE_GRADES_TABLE_NO_TABLE, "html.parser")
        grades = _parse_grade_table(soup)
        assert grades == []
