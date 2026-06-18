import os
import re
import uuid

# Absolute, resolved base — no ".." tricks can escape this
STORAGE_BASE = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "storage")
)

# Allowlist: uuid4().hex is always exactly 32 lowercase hex chars.
# Dots, slashes, null bytes, unicode — all rejected before any path is built.
_SAFE_ID = re.compile(r"^[0-9a-f]{32}$")


def _safe_path(subdir: str, image_id: str, suffix: str = "") -> str:
    """
    Build and validate a storage path for a given image_id.

    Two-layer defence:
      1. Regex allowlist — only 32-char hex strings pass (uuid4().hex format).
      2. realpath containment check — resolves symlinks and any residual '..'
         before asserting the result is still inside STORAGE_BASE.

    Raises ValueError for any input that fails either check.
    """
    if not _SAFE_ID.match(image_id):
        raise ValueError(f"Invalid image_id: {image_id!r}")

    candidate = os.path.realpath(
        os.path.join(STORAGE_BASE, subdir, image_id + suffix)
    )
    base = os.path.realpath(STORAGE_BASE)

    # os.sep suffix prevents "/storage-evil" from matching "/storage"
    if not candidate.startswith(base + os.sep):
        raise ValueError("Path traversal detected")

    return candidate


def generate_id() -> str:
    """Generate a unique ID for an image session (always satisfies _SAFE_ID)."""
    return uuid.uuid4().hex


def get_encrypted_path(image_id: str, ext: str) -> str:
    """Return the validated path for an encrypted file (write side)."""
    # ext is derived from the uploaded filename server-side, not from user input,
    # but strip anything that looks like a directory component just in case.
    safe_ext = os.path.basename(ext)
    return _safe_path("encrypted", image_id, safe_ext + ".enc")


def get_recovered_path(image_id: str, ext: str) -> str:
    """Return the validated path for a recovered (decrypted) file."""
    safe_ext = os.path.basename(ext)
    return _safe_path("recovered", image_id, safe_ext)


def save_bytes(path: str, data: bytes) -> None:
    """Write bytes to an already-validated path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def read_bytes(path: str) -> bytes:
    """Read bytes from an already-validated path."""
    with open(path, "rb") as f:
        return f.read()


def find_encrypted_file(image_id: str) -> str:
    """
    Locate the encrypted file for image_id without using glob on raw user input.

    Strategy: list the encrypted directory and filter in Python after validating
    image_id. This means the filesystem never receives a user-controlled pattern.

    Returns the full path if exactly one match is found.
    Raises ValueError for an invalid image_id.
    Raises FileNotFoundError if no matching file exists.
    """
    if not _SAFE_ID.match(image_id):
        raise ValueError(f"Invalid image_id: {image_id!r}")

    encrypted_dir = os.path.realpath(os.path.join(STORAGE_BASE, "encrypted"))
    base = os.path.realpath(STORAGE_BASE)

    try:
        entries = os.listdir(encrypted_dir)
    except FileNotFoundError:
        raise FileNotFoundError(f"Encrypted storage directory not found: {encrypted_dir}")

    matches = []
    for entry in entries:
        if entry.startswith(image_id) and entry.endswith(".enc"):
            candidate = os.path.realpath(os.path.join(encrypted_dir, entry))
            # Containment check on every entry — belt and braces
            if candidate.startswith(base + os.sep):
                matches.append(candidate)

    if not matches:
        raise FileNotFoundError(f"No encrypted image found for image_id={image_id!r}")

    # Deterministic: there should only ever be one file per image_id
    return matches[0]