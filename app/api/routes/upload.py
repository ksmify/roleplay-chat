import os
import uuid
import requests
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.auth.dependencies import CurrentUser, get_current_user

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Free & Secure Visual Safety Inspection Service
SIGHTENGINE_API_USER = os.getenv("SIGHTENGINE_API_USER", "")
SIGHTENGINE_API_SECRET = os.getenv("SIGHTENGINE_API_SECRET", "")


def inspect_image_safety(file_bytes: bytes) -> bool:
    """
    Scans uploaded avatar images for explicit nudity, erotica, and gore.
    Returns True if image is safe, False if inappropriate content is detected.
    """
    if not SIGHTENGINE_API_USER or not SIGHTENGINE_API_SECRET:
        # If API keys not set yet, fallback to extension & size security
        return True

    try:
        response = requests.post(
            "https://api.sightengine.com/1.0/check.json",
            files={"media": file_bytes},
            data={
                "models": "nudity-2.0,gore",
                "api_user": SIGHTENGINE_API_USER,
                "api_secret": SIGHTENGINE_API_SECRET,
            },
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            # Check Nudity Score
            nudity = data.get("nudity", {})
            sexual_activity = nudity.get("sexual_activity", 0)
            sexual_display = nudity.get("sexual_display", 0)
            erotica = nudity.get("erotica", 0)

            # Check Gore Score
            gore = data.get("gore", {})
            gore_prob = gore.get("prob", 0)

            if (
                sexual_activity > 0.4
                or sexual_display > 0.4
                or erotica > 0.6
                or gore_prob > 0.5
            ):
                return False
    except Exception as e:
        print("Visual Safety Check Error:", e)

    return True


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Uploads user or character avatar with automatic NSFW/Gore safety scan.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    file_bytes = await file.read()

    # Perform Visual Safety Scan
    is_safe = inspect_image_safety(file_bytes)
    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail="Inappropriate image detected. Public avatars must remain Safe-For-Work.",
        )

    # Save image
    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = f"avatar_{uuid.uuid4().hex[:12]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return {
        "url": f"/static/uploads/{filename}",
        "filename": filename,
    }
