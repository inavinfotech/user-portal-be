from fastapi import Depends, HTTPException, status, Security
from typing import List, Optional

from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from app.services.application_service import application_service
from app.models.application import Application
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User
from app.services.auth_service import auth_service
from app.schemas.user import User as UserSchema
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(db: Session = Depends(get_db), payload: dict = Depends(get_token_payload)) -> User:
    user_id: str = payload.get("sub")
    token_jti: str = payload.get("jti")
    if user_id is None or token_jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Check if session is active in DB
    if not auth_service.is_session_active(db, token_jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalidated",
        )
        
    user = db.query(User).filter(User.id == uuid.UUID(user_id), User.is_deleted == False).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

class PermissionChecker:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        for role in current_user.roles:
            for perm in role.permissions:
                if perm.resource == self.resource and perm.action == self.action:
                    return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions for {self.action} on {self.resource}"
        )

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        for role in current_user.roles:
            if role.name in self.allowed_roles:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have any of the allowed roles: {self.allowed_roles}"
        )


api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
api_secret_header = APIKeyHeader(name="X-API-SECRET", auto_error=False)

def verify_api_key(db: Session = Depends(get_db), api_key: str = Security(api_key_header)) -> bool:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    
    app = application_service.get_application_by_key(db, api_key)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API key",
        )
    return True

def verify_api_credentials(
    db: Session = Depends(get_db), 
    api_key: str = Security(api_key_header),
    api_secret: str = Security(api_secret_header)
) -> Application:
    if not api_key or not api_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key or Secret",
        )
    
    app = application_service.verify_api_secret(db, api_key, api_secret)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Credentials",
        )
    return app
