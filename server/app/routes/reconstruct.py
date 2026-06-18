import logging
import mimetypes
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.db import get_sessions_collection
from app.crypto.aes import decrypt_data
from app.crypto.shares import recover_key
from app.utils.file_handler import (
    find_encrypted_file,
    get_recovered_path,
    save_bytes,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class ReconstructRequest(BaseModel):
    image_id: str
    shares: list[str]


@router.post("/reconstruct")
async def reconstruct_image(payload: ReconstructRequest):
    if len(payload.shares) < 3:
        raise HTTPException(status_code=400, detail="At least 3 shares are required")

    # Locate the encrypted file safely.
    # find_encrypted_file() validates image_id via regex allowlist, lists the
    # directory in Python, and performs a realpath containment check on every
    # candidate — user-supplied image_id never reaches glob() or open() directly.
    try:
        encrypted_path = find_encrypted_file(payload.image_id)
    except ValueError:
        # Invalid image_id format — treat as not found so we don't leak
        # information about the validation logic to the caller.
        raise HTTPException(status_code=404, detail="No encrypted image found for this image_id")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No encrypted image found for this image_id")

    encrypted_filename = os.path.basename(encrypted_path)

    # Strip ".enc" to recover the original "<id><ext>" filename
    # e.g. "ab12cd34ef....png.enc" -> "ab12cd34ef....png"
    if not encrypted_filename.endswith(".enc"):
        raise HTTPException(status_code=500, detail="Unexpected storage format")

    original_filename = encrypted_filename[:-4]  # drop trailing ".enc"

    # Derive the extension for the recovered file path
    # original_filename is "<image_id><ext>", so splitext gives us "<ext>"
    _, ext = os.path.splitext(original_filename)

    with open(encrypted_path, "rb") as f:
        encrypted_bytes = f.read()

    try:
        key = recover_key(payload.shares)
        plaintext = decrypt_data(encrypted_bytes, key)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Failed to reconstruct — shares may be invalid or corrupted",
        )

    # Build a validated path for the recovered file and persist it.
    try:
        recovered_path = get_recovered_path(payload.image_id, ext)
    except ValueError as exc:
        logger.error("Path validation failed during reconstruct: %s", exc)
        raise HTTPException(status_code=500, detail="Internal error generating recovery path")

    save_bytes(recovered_path, plaintext)

    _mark_reconstructed(payload.image_id)

    media_type = mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
    return Response(content=plaintext, media_type=media_type)


def _mark_reconstructed(image_id: str) -> None:
    """Best-effort audit update. Never lets a Mongo failure affect the response —
    the image has already been decrypted and is on its way back to the client."""
    try:
        get_sessions_collection().update_one(
            {"image_id": image_id},
            {
                "$set": {"last_reconstructed_at": datetime.utcnow()},
                "$inc": {"reconstruct_count": 1},
            },
        )
    except Exception:
        logger.warning(
            "Failed to update reconstruct audit fields for image_id=%s. "
            "Reconstruction itself succeeded and was unaffected.",
            image_id,
            exc_info=True,
        )