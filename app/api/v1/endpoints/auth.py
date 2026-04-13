from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import auth_service
from app.core import security
from app.schemas.user import User as UserSchema
from app.api import deps

router = APIRouter()

@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    session = auth_service.create_session(db, user_id=user.id)
    
    access_token = security.create_access_token(
        data={"sub": str(user.id), "jti": session.token_jti, "roles": [role.name for role in user.roles]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(db: Session = Depends(get_db), current_user: UserSchema = Depends(deps.get_current_user), token_payload: dict = Depends(deps.get_token_payload)):
    token_jti = token_payload.get("jti")
    if token_jti:
        auth_service.invalidate_session(db, token_jti)
    return {"detail": "Logged out successfully"}
