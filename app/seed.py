import os
import logging
from app.database import SessionLocal
from app.models import User
from app.auth import hash_password

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "musbi")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "musbi123")
DEFAULT_ADMIN_FULLNAME = os.environ.get("ADMIN_FULLNAME", "Musbi")


def seed_admin_user():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.commit()
                logger.info("Existing user promoted to admin: %s", DEFAULT_ADMIN_USERNAME)
            else:
                logger.info("Admin user already exists: %s", DEFAULT_ADMIN_USERNAME)
            return

        user = User(
            username=DEFAULT_ADMIN_USERNAME,
            password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            full_name=DEFAULT_ADMIN_FULLNAME,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        logger.info("Default admin user created: %s", DEFAULT_ADMIN_USERNAME)
    except Exception as e:
        logger.error("Failed to seed admin user: %s", e)
        db.rollback()
    finally:
        db.close()
