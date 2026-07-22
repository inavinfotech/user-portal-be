import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import Session as UserSession
from app.core import security
from app.schemas.user import UserCreate

class AuthService:
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            return None
        if not security.verify_password(password, db_user.hashed_password):
            return None

        # Auto-recover soft-deleted user if correct password is provided
        if db_user.is_deleted:
            db_user.is_deleted = False
            db_user.is_active = True
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        return db_user

    def create_session(self, db: Session, user_id: uuid.UUID, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> UserSession:
        session_id = uuid.uuid4()
        token_jti = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=30) # Match JWT expiry
        
        db_session = UserSession(
            id=session_id,
            user_id=user_id,
            token_jti=token_jti,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    def invalidate_session(self, db: Session, token_jti: str) -> bool:
        db_session = db.query(UserSession).filter(UserSession.token_jti == token_jti).first()
        if db_session:
            db_session.is_deleted = True # Using soft delete as per base mixin
            db.commit()
            return True
        return False

    def is_session_active(self, db: Session, token_jti: str) -> bool:
        db_session = db.query(UserSession).filter(
            UserSession.token_jti == token_jti,
            UserSession.is_deleted == False,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        return db_session is not None

    def get_user_sessions(self, db: Session, user_id: uuid.UUID) -> List[UserSession]:
        return db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_deleted == False,
            UserSession.expires_at > datetime.utcnow()
        ).all()

    def revoke_session(self, db: Session, user_id: uuid.UUID, token_jti: str) -> bool:
        db_session = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.token_jti == token_jti,
            UserSession.is_deleted == False
        ).first()
        if db_session:
            db_session.is_deleted = True
            db.commit()
            return True
        return False

auth_service = AuthService()
