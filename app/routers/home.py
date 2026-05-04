from datetime import datetime
from fastapi import APIRouter
from app.schemas import HomeResponse

router = APIRouter(tags=["Home"])

#testing why the home route is not working, it should return a simple welcome message and timestamp

@router.get("/", response_model=HomeResponse)
async def home():
    return HomeResponse(message="Welcome to the Fire Alert System API!", timestamp=datetime.utcnow().isoformat())



