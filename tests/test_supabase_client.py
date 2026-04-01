import pytest
from unittest.mock import patch, MagicMock
from services.supabase_client import get_supabase_client


def test_get_supabase_client_success():
    fake_client = MagicMock()

    with patch("services.supabase_client.Config.SUPABASE_URL", "https://example.supabase.co"), \
         patch("services.supabase_client.Config.SUPABASE_KEY", "fake-key"), \
         patch("services.supabase_client.create_client", return_value=fake_client) as mock_create:

        client = get_supabase_client()

        mock_create.assert_called_once_with("https://example.supabase.co", "fake-key")
        assert client == fake_client


def test_get_supabase_client_missing_url():
    with patch("services.supabase_client.Config.SUPABASE_URL", None), \
         patch("services.supabase_client.Config.SUPABASE_KEY", "fake-key"):

        with pytest.raises(ValueError, match="Missing Supabase configuration"):
            get_supabase_client()


def test_get_supabase_client_missing_key():
    with patch("services.supabase_client.Config.SUPABASE_URL", "https://example.supabase.co"), \
         patch("services.supabase_client.Config.SUPABASE_KEY", None):

        with pytest.raises(ValueError, match="Missing Supabase configuration"):
            get_supabase_client()