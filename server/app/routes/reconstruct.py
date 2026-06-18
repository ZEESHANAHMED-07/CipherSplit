import glob
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
from app.utils.file_handler import STORAGE_BASE, save_bytes

router = APIRouter()
logger = logging.getLogger(__name__)


class ReconstructRequest(BaseModel):
    image_id: str
    shares: list[str]


@router.post("/reconstruct")
async def reconstruct_image(payload: ReconstructRequest):
    if len(payload.shares) < 3:
        raise HTTPException(status_code=400, detail="At least 3 shares are required")

    # The encrypted file on disk is the source of truth, not MongoDB.
    # Filenames are deterministic ("<image_id><ext>.enc"), so reconstruction
    # has to work even if Mongo is completely unreachable — the crypto core
    # doesn't depend on the database, only the audit trail does.
    encrypted_dir = os.path.join(STORAGE_BASE, "encrypted")
    matches = glob.glob(os.path.join(encrypted_dir, f"{payload.image_id}*.enc"))

    if not matches:
        raise HTTPException(status_code=404, detail="No encrypted image found for this image_id")

    encrypted_path = matches[0]
    encrypted_filename = os.path.basename(encrypted_path)
    original_filename = encrypted_filename[:-4]  # strip trailing ".enc"

    with open(encrypted_path, "rb") as f:
        encrypted_bytes = f.read()

    try:
        key = recover_key(payload.shares)
        plaintext = decrypt_data(encrypted_bytes, key)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to reconstruct — shares may be invalid")

    recovered_path = os.path.join(STORAGE_BASE, "recovered", original_filename)
    save_bytes(recovered_path, plaintext)

    _mark_reconstructed(payload.image_id)

    media_type = mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
    return Response(content=plaintext, media_type=media_type)


def _mark_reconstructed(image_id: str) -> None:
    """Best-effort audit update. Never let a Mongo failure affect the
    response — the image has already been decrypted and is on its way
    back to the client by the time this runs."""
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