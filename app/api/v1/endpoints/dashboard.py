from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary, ActivityItem
from app.models.user import User
from app.models.auth import Role
from app.models.application import Application
from app.models.session import Session as UserSession
from app.api import deps

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db), current_user = Depends(deps.RoleChecker(["admin"]))):

    total_users = db.query(User).count()
    total_roles = db.query(Role).count()
    total_applications = db.query(Application).count()
    active_sessions = db.query(UserSession).filter(
        UserSession.is_deleted == False,
        UserSession.expires_at > datetime.utcnow()
    ).count()

    # Get recent activity (e.g., last 5 applications registered)
    recent_apps = db.query(Application).order_by(Application.created_at.desc()).limit(5).all()
    recent_activity = []
    for app in recent_apps:
        recent_activity.append(ActivityItem(
            id=str(app.id),
            type="APPLICATION_REGISTERED",
            description=f"New application registered: {app.name}",
            timestamp=app.created_at
        ))
    
    # If no apps, maybe add some recent users
    if not recent_activity:
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        for user in recent_users:
            recent_activity.append(ActivityItem(
                id=str(user.id),
                type="USER_REGISTERED",
                description=f"New user registered: {user.full_name or user.email}",
                timestamp=user.created_at
            ))

    return DashboardSummary(
        total_users=total_users,
        total_roles=total_roles,
        total_applications=total_applications,
        active_sessions=active_sessions,
        recent_activity=recent_activity
    )
