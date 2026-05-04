from datetime import datetime
from fastapi import APIRouter
from app.schemas import HomeResponse

router = APIRouter(tags=["Home"])

@router.get("/", response_model=HomeResponse)
async def home():
    return HomeResponse(message="Welcome to the Fire Alert System API!", timestamp=datetime.utcnow().isoformat())



