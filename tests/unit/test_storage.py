import json

from src.storage import find_new_grades, load_known_grades, save_grades


class TestFindNewGrades:
    def test_all_new(self, sample_grades):
        result = find_new_grades(sample_grades, [])
        assert result == sample_grades

    def test_no_new(self, sample_grades):
        result = find_new_grades(sample_grades, sample_grades)
        assert result == []

    def test_partial_new(self, sample_grades, sample_grades_with_new):
        result = find_new_grades(sample_grades_with_new, sample_grades)
        assert len(result) == 1
        assert result[0]["name"] == "Softwaretechnik"

    def test_grade_change_detected(self, sample_grades):
        changed = [
            {"name": "Einführung in die Informatik", "grade": "1,0", "credits": "6,0"},
            {"name": "Datenbanken", "grade": "2,0", "credits": "9,0"},
        ]
        result = find_new_grades(changed, sample_grades)
        assert len(result) == 1
        assert result[0]["grade"] == "1,0"


class TestJsonPersistence:
    def test_save_and_load(self, tmp_path, monkeypatch, sample_grades):
        monkeypatch.setattr("src.storage.DATA_DIR", tmp_path)
        monkeypatch.setattr("src.storage.GRADES_FILE", tmp_path / "grades.json")

        save_grades(sample_grades)
        loaded = load_known_grades()
        assert loaded == sample_grades

    def test_load_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.storage.GRADES_FILE", tmp_path / "nonexistent.json")
        assert load_known_grades() == []

    def test_load_corrupt_file(self, tmp_path, monkeypatch):
        corrupt_file = tmp_path / "grades.json"
        corrupt_file.write_text("not valid json", encoding="utf-8")
        monkeypatch.setattr("src.storage.GRADES_FILE", corrupt_file)
        assert load_known_grades() == []

    def test_save_creates_directory(self, tmp_path, monkeypatch, sample_grades):
        new_dir = tmp_path / "subdir"
        monkeypatch.setattr("src.storage.DATA_DIR", new_dir)
        monkeypatch.setattr("src.storage.GRADES_FILE", new_dir / "grades.json")

        save_grades(sample_grades)
        assert (new_dir / "grades.json").exists()

    def test_json_format(self, tmp_path, monkeypatch, sample_grades):
        monkeypatch.setattr("src.storage.DATA_DIR", tmp_path)
        grades_file = tmp_path / "grades.json"
        monkeypatch.setattr("src.storage.GRADES_FILE", grades_file)

        save_grades(sample_grades)

        raw = grades_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        assert data == sample_grades
        assert "Einführung" in raw  # ensure_ascii=False works
