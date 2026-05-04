from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, FireReport as FireReportModel
from app.schemas import FireReport, UpdateStatusRequest, AdminStats
from app.auth import require_admin

router = APIRouter(tags=["admin"])


def _serialize(report: FireReportModel, user: Optional[User]) -> FireReport:
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


@router.get("/reports", response_model=List[FireReport])
def get_admin_reports(
    status: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(FireReportModel)

    if status:
        query = query.filter(FireReportModel.status == status)

    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            query = query.filter(FireReportModel.created_at > since_dt)
        except ValueError:
            pass

    reports = query.order_by(FireReportModel.created_at.desc()).all()

    user_ids = {r.user_id for r in reports}
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    return [_serialize(r, users.get(r.user_id)) for r in reports]


@router.patch("/reports/{report_id}/status", response_model=FireReport)
def update_report_status(
    report_id: int,
    body: UpdateStatusRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    report = db.query(FireReportModel).filter(FireReportModel.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "message": "Report not found"},
        )

    report.status = body.status.value
    if body.notes is not None:
        report.notes = body.notes
    report.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(report)

    user = db.query(User).filter(User.id == report.user_id).first()
    return _serialize(report, user)


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    all_reports = db.query(FireReportModel.status).all()
    statuses = [r.status for r in all_reports]

    return AdminStats(
        total=len(statuses),
        pending=statuses.count("pending"),
        inProgress=statuses.count("in-progress"),
        resolved=statuses.count("resolved"),
    )
