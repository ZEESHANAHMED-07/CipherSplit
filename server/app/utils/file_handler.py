import os
import uuid

# Points to backend/storage
STORAGE_BASE = os.path.join(os.path.dirname(__file__), "..", "..", "storage")


def generate_id() -> str:
    """Generate a unique ID for an image session."""
    return uuid.uuid4().hex


def save_bytes(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()