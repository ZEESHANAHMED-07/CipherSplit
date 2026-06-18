import logging
import os
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.db import get_sessions_collection
from app.crypto.aes import generate_key, encrypt_data
from app.crypto.shares import split_key
from app.utils.file_handler import STORAGE_BASE, save_bytes, generate_id

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/encrypt")
async def encrypt_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    # Unique ID for this encryption session, keeps original extension for later
    image_id = generate_id()
    ext = os.path.splitext(file.filename)[1]  # e.g. ".png"

    # AES-256 encrypt the image
    key = generate_key()
    encrypted_bytes = encrypt_data(image_bytes, key)

    # Save encrypted file as <id><ext>.enc, e.g. ab12cd34.png.enc
    encrypted_filename = f"{image_id}{ext}.enc"
    encrypted_path = os.path.join(STORAGE_BASE, "encrypted", encrypted_filename)
    save_bytes(encrypted_path, encrypted_bytes)

    # Split the AES key into 5 shares, 3 needed to recover
    shares = split_key(key, threshold=3, num_shares=5)

    # Persist session METADATA only. Shares are deliberately NOT stored here:
    # all 5 living in one place would defeat the point of splitting the key,
    # anyone with DB access could reconstruct it without needing 3 separate
    # holders. The DB is for tracking/audit, not part of the crypto trust model.
    #
    # This is also wrapped in try/except on purpose: if Mongo is unreachable
    # (auth issue, network, TLS, whatever), encryption still has to succeed.
    # The DB write is a side effect, not a dependency of the core flow.
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
        "shares": shares
    })