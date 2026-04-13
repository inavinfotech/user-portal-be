from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api import deps
from app.services.auth_service import auth_service
from app.schemas.session import Session as SessionSchema, SessionRevoke
from app.models.user import User

router = APIRouter()

@router.get("/active", response_model=List[SessionSchema])
def get_active_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    sessions = auth_service.get_user_sessions(db, user_id=current_user.id)
    return sessions

@router.post("/revoke", response_model=dict)
def revoke_session(
    revoke_in: SessionRevoke,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    success = auth_service.revoke_session(db, user_id=current_user.id, token_jti=revoke_in.token_jti)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or already revoked")
    return {"detail": "Session revoked successfully"}
