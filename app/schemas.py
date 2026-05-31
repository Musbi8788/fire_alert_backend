from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ReportStatus(StrEnum):
    pending = "pending"
    in_progress = "in-progress"
    resolved = "resolved"


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    fullName: str
    phone: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    id: int
    username: str
    fullName: str
    phone: str | None = None
    isAdmin: bool
    createdAt: str


class AuthResponse(BaseModel):
    token: str
    user: UserProfile


class CreateReportRequest(BaseModel):
    description: str = Field(min_length=10)
    latitude: float
    longitude: float
    address: str | None = None


class FireReport(BaseModel):
    id: int
    userId: int
    username: str
    fullName: str
    phone: str | None = None
    description: str
    latitude: float
    longitude: float
    address: str | None = None
    status: str
    createdAt: str
    updatedAt: str


class UpdateStatusRequest(BaseModel):
    status: ReportStatus
    notes: str | None = None


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


class HomeResponse(BaseModel):
    message: str
    timestamp: datetime
