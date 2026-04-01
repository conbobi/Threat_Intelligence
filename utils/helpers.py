import hashlib
from urllib.parse import urlparse

def normalize_url(url: str) -> str:
    if not url:
        return ""

    url = url.strip()
    parsed = urlparse(url)

    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    return f"{scheme}://{netloc}{path}" if path else f"{scheme}://{netloc}"

def hash_file(file_path: str, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()