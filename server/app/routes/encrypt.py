import logging
import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.db import get_sessions_collection
from app.crypto.aes import generate_key, encrypt_data
from app.crypto.shares import split_key
from app.utils.file_handler import (
    generate_id,
    get_encrypted_path,
    save_bytes,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/encrypt")
async def encrypt_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    # Unique ID for this encryption session
    image_id = generate_id()

    # Extension is derived from the server-received filename, not from any
    # user-controlled path component. get_encrypted_path() sanitises it too.
    ext = os.path.splitext(file.filename)[1]  # e.g. ".png"

    # AES-256-GCM encrypt the image
    key = generate_key()
    encrypted_bytes = encrypt_data(image_bytes, key)

    # Build and validate the storage path, then write.
    # get_encrypted_path() enforces the regex allowlist + realpath containment
    # check — a ValueError here would mean generate_id() produced something
    # unexpected, which should never happen in practice.
    try:
        encrypted_path = get_encrypted_path(image_id, ext)
    except ValueError as exc:
        logger.error("Path validation failed during encrypt: %s", exc)
        raise HTTPException(status_code=500, detail="Internal error generating storage path")

    save_bytes(encrypted_path, encrypted_bytes)
    encrypted_filename = os.path.basename(encrypted_path)

    # Split the AES key into 5 shares, 3 needed to recover
    shares = split_key(key, threshold=3, num_shares=5)

    # Persist session METADATA only — shares are deliberately never stored here.
    # All 5 shares living in one place would defeat the point of key splitting:
    # anyone with DB access could reconstruct the key without needing 3 separate
    # holders. The DB is an audit/tracking layer, not part of the crypto trust model.
    #
    # Wrapped in try/except intentionally: if Mongo is unreachable (auth, network,
    # TLS, etc.) encryption must still succeed. The DB write is a side effect,
    # not a dependency of the core flow.
    try:
        get_sessions_collection().insert_one({
            "image_id": image_id,
            "original_filename": file.filename,
            "encrypted_filename": encrypted_filename,
            "encrypted_path": encrypted_path,
            "threshold": 3,
            "total_shares": 5,
        })
    except Exception:
        logger.warning(
            "Failed to write session metadata to MongoDB for image_id=%s. "
            "Encryption still succeeded; this only affects tracking/audit.",
            image_id,
            exc_info=True,
        )

    return JSONResponse({
        "image_id": image_id,
        "threshold": 3,
        "total_shares": 5,
        "shares": shares,
    })