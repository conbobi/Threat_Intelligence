from utils.validators import is_valid_url, is_valid_email, is_allowed_file


def test_is_valid_url_accepts_http():
    assert is_valid_url("http://example.com") is True


def test_is_valid_url_accepts_https():
    assert is_valid_url("https://example.com/path") is True


def test_is_valid_url_rejects_invalid_url():
    assert is_valid_url("abc") is False
    assert is_valid_url("ftp://example.com") is False
    assert is_valid_url("") is False


def test_is_valid_email_accepts_valid_email():
    assert is_valid_email("user@example.com") is True
    assert is_valid_email("user.name+1@example.com") is True


def test_is_valid_email_rejects_invalid_email():
    assert is_valid_email("userexample.com") is False
    assert is_valid_email("user@") is False
    assert is_valid_email("") is False


def test_is_allowed_file_accepts_valid_extensions():
    assert is_allowed_file("file.pdf") is True
    assert is_allowed_file("note.txt") is True
    assert is_allowed_file("image.jpg") is True
    assert is_allowed_file("image.png") is True


def test_is_allowed_file_rejects_invalid_extensions():
    assert is_allowed_file("script.exe") is False
    assert is_allowed_file("archive.zip") is False
    assert is_allowed_file("nofileextension") is False
    assert is_allowed_file("") is False