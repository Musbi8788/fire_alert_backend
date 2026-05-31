from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import hash_password, sign_token, verify_password
from app.database import get_db
from app.models import User
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, UserProfile

router = APIRouter(tags=["auth"])


def _user_profile(user: User) -> UserProfile:
    return UserProfile(
        id=user.id,
        username=user.username,
        fullName=user.full_name,
        phone=user.phone,
        isAdmin=user.is_admin,
        createdAt=user.created_at.isoformat(),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Conflict", "message": "Username already taken"},
        )

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        full_name=body.fullName,
        phone=body.phone,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = sign_token(user.id, user.username, user.is_admin)
    return AuthResponse(token=token, user=_user_profile(user))


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Unauthorized", "message": "Invalid credentials"},
        )

    token = sign_token(user.id, user.username, user.is_admin)
    return AuthResponse(token=token, user=_user_profile(user))
