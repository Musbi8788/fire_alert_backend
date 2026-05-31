
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_auth
from app.database import get_db
from app.models import FireReport as FireReportModel
from app.models import User
from app.schemas import CreateReportRequest, FireReport

router = APIRouter(tags=["reports"])


def _serialize(report: FireReportModel, user: User) -> FireReport:
    return FireReport(
        id=report.id,
        userId=report.user_id,
        username=user.username if user else "",
        fullName=user.full_name if user else "",
        phone=user.phone if user else None,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        address=report.address,
        status=report.status,
        createdAt=report.created_at.isoformat(),
        updatedAt=report.updated_at.isoformat(),
    )


@router.post("", response_model=FireReport, status_code=201)
def create_report(
    body: CreateReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    report = FireReportModel(
        user_id=current_user.id,
        description=body.description,
        latitude=body.latitude,
        longitude=body.longitude,
        address=body.address,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return _serialize(report, current_user)


@router.get("", response_model=list[FireReport])
def get_user_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    reports = (
        db.query(FireReportModel)
        .filter(FireReportModel.user_id == current_user.id)
        .order_by(FireReportModel.created_at)
        .all()
    )
    return [_serialize(r, current_user) for r in reports]
