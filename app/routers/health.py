from fastapi import APIRouter

from app.schemas import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthStatus)
async def health_check():
    return {"status": "ok"}
