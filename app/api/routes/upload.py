import os
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed",
        )

    file_extension = Path(file.filename or "image.png").suffix
    if not file_extension:
        file_extension = ".png"

    unique_filename = f"avatar_{uuid.uuid4().hex[:12]}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    contents = await file.read()
    with file_path.open("wb") as f:
        f.write(contents)

    relative_url = f"/static/uploads/{unique_filename}"
    return {
        "url": relative_url,
        "avatar_url": relative_url,
    }
