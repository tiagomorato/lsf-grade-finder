import pytest

from src.config import load_config


@pytest.fixture
def full_env(monkeypatch):
    """Set all required environment variables."""
    env_vars = {
        "LSF_BASE_URL": "https://lsf.example.com/",
        "LSF_USERNAME": "testuser",
        "LSF_PASSWORD": "testpass",
        "TELEGRAM_BOT_TOKEN": "123:ABC",
        "TELEGRAM_CHAT_ID": "456",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


def test_load_config_success(full_env):
    config = load_config()
    assert config["lsf_base_url"] == "https://lsf.example.com/"
    assert config["lsf_username"] == "testuser"
    assert config["run_mode"] == "once"
    assert config["check_interval_minutes"] == 30


def test_load_config_missing_required_var(full_env, monkeypatch):
    monkeypatch.delenv("LSF_USERNAME")
    with pytest.raises(SystemExit):
        load_config()


def test_load_config_invalid_run_mode(full_env, monkeypatch):
    monkeypatch.setenv("RUN_MODE", "invalid")
    with pytest.raises(SystemExit):
        load_config()


def test_load_config_custom_interval(full_env, monkeypatch):
    monkeypatch.setenv("CHECK_INTERVAL_MINUTES", "15")
    config = load_config()
    assert config["check_interval_minutes"] == 15


def test_load_config_invalid_interval(full_env, monkeypatch):
    monkeypatch.setenv("CHECK_INTERVAL_MINUTES", "not_a_number")
    with pytest.raises(SystemExit):
        load_config()


def test_load_config_loop_mode(full_env, monkeypatch):
    monkeypatch.setenv("RUN_MODE", "loop")
    config = load_config()
    assert config["run_mode"] == "loop"
