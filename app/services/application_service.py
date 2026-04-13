import secrets
import string
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.application import Application
from app.schemas.application import ApplicationCreate
from typing import List, Optional
from uuid import UUID

from app.core.security import get_password_hash, verify_password

def generate_secure_api_secret(length: int = 40) -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))

def generate_client_id(length: int = 24) -> str:
    return "app_" + secrets.token_hex(length // 2)

class ApplicationService:
    def register_application(self, db: Session, app_in: ApplicationCreate) -> tuple[Application, str]:
        # Check for existing name
        existing_app = db.query(Application).filter(Application.name == app_in.name, Application.is_deleted == False).first()
        if existing_app:
            raise HTTPException(status_code=400, detail="Application with this name already exists")
            
        client_id = generate_client_id()

        api_secret = generate_secure_api_secret()
        api_secret_hash = get_password_hash(api_secret)
        
        db_app = Application(
            name=app_in.name,
            description=app_in.description,
            client_id=client_id,
            api_secret_hash=api_secret_hash,
            is_active=app_in.is_active
        )
        db.add(db_app)
        db.commit()
        db.refresh(db_app)
        return db_app, api_secret

    def regenerate_api_secret(self, db: Session, client_id: str) -> tuple[Optional[Application], Optional[str]]:
        db_app = db.query(Application).filter(Application.client_id == client_id).first()
        if db_app:
            api_secret = generate_secure_api_secret()
            db_app.api_secret_hash = get_password_hash(api_secret)
            db.commit()
            db.refresh(db_app)
            return db_app, api_secret
        return None, None


    def get_application_by_key(self, db: Session, api_key: str) -> Optional[Application]:
        return db.query(Application).filter(Application.client_id == api_key, Application.is_active == True).first()

    def verify_api_secret(self, db: Session, client_id: str, api_secret: str) -> Optional[Application]:
        app = self.get_application_by_key(db, client_id)
        if app and verify_password(api_secret, app.api_secret_hash):
            return app
        return None

    def get_applications(self, db: Session, skip: int = 0, limit: int = 100) -> List[Application]:
        return db.query(Application).offset(skip).limit(limit).all()

    def delete_application(self, db: Session, app_id: UUID) -> bool:
        db_app = db.query(Application).filter(Application.id == app_id).first()
        if db_app:
            db.delete(db_app)
            db.commit()
            return True
        return False

application_service = ApplicationService()

