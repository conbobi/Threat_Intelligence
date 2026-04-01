import hashlib
from utils.helpers import normalize_url, hash_file


def test_normalize_url_adds_https_when_missing():
    assert normalize_url("example.com") == "https://example.com"


def test_normalize_url_lowercases_scheme_and_domain():
    assert normalize_url("HTTPS://EXAMPLE.COM") == "https://example.com"


def test_normalize_url_removes_trailing_slash():
    assert normalize_url("https://example.com/") == "https://example.com"


def test_normalize_url_keeps_path():
    assert normalize_url("https://example.com/login/page/") == "https://example.com/login/page"


def test_normalize_url_handles_empty_string():
    assert normalize_url("") == ""


def test_hash_file_sha256(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world", encoding="utf-8")

    expected = hashlib.sha256(b"hello world").hexdigest()
    result = hash_file(str(file_path), "sha256")

    assert result == expected


def test_hash_file_md5(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world", encoding="utf-8")

    expected = hashlib.md5(b"hello world").hexdigest()
    result = hash_file(str(file_path), "md5")

    assert result == expected