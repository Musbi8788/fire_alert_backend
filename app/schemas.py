from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class ReportStatus(str, Enum):
    pending = "pending"
    in_progress = "in-progress"
    resolved = "resolved"


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    fullName: str
    phone: Optional[int] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    id: int
    username: str
    fullName: str
    phone: Optional[str] = None
    isAdmin: bool
    createdAt: str


class AuthResponse(BaseModel):
    token: str
    user: UserProfile


class CreateReportRequest(BaseModel):
    description: str = Field(min_length=10)
    latitude: float
    longitude: float
    address: Optional[str] = None


class FireReport(BaseModel):
    id: int
    userId: int
    username: str
    fullName: str
    phone: Optional[str] = None
    description: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    status: str
    createdAt: str
    updatedAt: str


class UpdateStatusRequest(BaseModel):
    status: ReportStatus
    notes: Optional[str] = None


class AdminStats(BaseModel):
    total: int
    pending: int
    inProgress: int
    resolved: int


class ErrorResponse(BaseModel):
    error: str
    message: str


class HealthStatus(BaseModel):
    status: str
