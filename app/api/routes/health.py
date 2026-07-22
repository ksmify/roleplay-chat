from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health", summary="Check API health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}