import importlib
from unittest.mock import patch
import config


def test_config_has_required_attributes():
    assert hasattr(config.Config, "SECRET_KEY")
    assert hasattr(config.Config, "UPLOAD_FOLDER")
    assert hasattr(config.Config, "SUPABASE_URL")
    assert hasattr(config.Config, "SUPABASE_KEY")
    assert hasattr(config.Config, "VIRUSTOTAL_API_KEY")
    assert hasattr(config.Config, "GOOGLE_SAFE_BROWSING_KEY")
    assert hasattr(config.Config, "URLSCAN_API_KEY")
    assert hasattr(config.Config, "ADMIN_EMAIL")
    assert hasattr(config.Config, "ADMIN_PASSWORD")


def test_config_reads_env_variables(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "supabase-test-key")
    monkeypatch.setenv("VIRUSTOTAL_API_KEY", "vt-test-key")
    monkeypatch.setenv("GOOGLE_SAFE_BROWSING_KEY", "gsb-test-key")
    monkeypatch.setenv("URLSCAN_API_KEY", "urlscan-test-key")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@test.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "12345678")

    importlib.reload(config)

    assert config.Config.SECRET_KEY == "unit-test-secret"
    assert config.Config.SUPABASE_URL == "https://example.supabase.co"
    assert config.Config.SUPABASE_KEY == "supabase-test-key"
    assert config.Config.VIRUSTOTAL_API_KEY == "vt-test-key"
    assert config.Config.GOOGLE_SAFE_BROWSING_KEY == "gsb-test-key"
    assert config.Config.URLSCAN_API_KEY == "urlscan-test-key"
    assert config.Config.ADMIN_EMAIL == "admin@test.com"
    assert config.Config.ADMIN_PASSWORD == "12345678"


def test_config_default_values_without_env_file(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("VIRUSTOTAL_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_SAFE_BROWSING_KEY", raising=False)
    monkeypatch.delenv("URLSCAN_API_KEY", raising=False)
    monkeypatch.delenv("ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    with patch("dotenv.load_dotenv", return_value=None):
        importlib.reload(config)

    assert config.Config.SECRET_KEY == "dev-secret-key"
    assert config.Config.UPLOAD_FOLDER == "temp_uploads"
    assert config.Config.SUPABASE_URL is None
    assert config.Config.SUPABASE_KEY is None
    assert config.Config.VIRUSTOTAL_API_KEY is None
    assert config.Config.GOOGLE_SAFE_BROWSING_KEY is None
    assert config.Config.URLSCAN_API_KEY is None
    assert config.Config.ADMIN_EMAIL == "admin@gmail.com"
    assert config.Config.ADMIN_PASSWORD == "123456"