from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column("password_hash", String, nullable=False)
    full_name = Column("full_name", String, nullable=False)
    phone = Column(String, nullable=True)
    is_admin = Column("is_admin", Boolean, default=False, nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)


class FireReport(Base):
    __tablename__ = "fire_reports"

    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, nullable=False)
