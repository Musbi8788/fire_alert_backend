import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import health, users, reports, admin, home
from app.seed import seed_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_admin_user()
    yield


app = FastAPI(
    title="Fire Alert Platform API",
    version="0.1.0",
    description="Fire Alert Platform API for The Gambia",
    lifespan=lifespan,
    redirect_slashes=False,
)

raw_origins = os.environ.get(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,https://fire-alert-mu.vercel.app",
)
allow_origins = [
    origin.strip().rstrip("/")
    for origin in raw_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=(
        r"^https?://(localhost|127\.0\.0\.1):\d+$"
        r"|^https://fire-alert-mu\.vercel\.app$"
        r"|^https://fire-alert-[a-z0-9-]+\.vercel\.app$"
    ),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router)
app.include_router(health.router, prefix="/api")
app.include_router(users.router, prefix="/api/users")
app.include_router(reports.router, prefix="/api/reports")
app.include_router(admin.router, prefix="/api/admin")
