from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db

from app.schemas.application import Application, ApplicationCreate, ApplicationOut, ApplicationCreateOut, ApplicationUpdate

from app.services.application_service import application_service
from app.api import deps

router = APIRouter()

@router.post("/", response_model=ApplicationCreateOut)
def register_application(app_in: ApplicationCreate, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):
    db_app, api_secret = application_service.register_application(db, app_in)
    # Convert SQLAlchemy model to dict and add the secret
    app_data = ApplicationOut.model_validate(db_app).model_dump()
    return ApplicationCreateOut(**app_data, api_secret=api_secret)

@router.put("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: UUID, 
    app_in: ApplicationUpdate, 
    db: Session = Depends(get_db), 
    current_admin = Depends(deps.RoleChecker(["admin"]))
):
    db_app = application_service.update_application(db, app_id=app_id, app_in=app_in)
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_app

@router.post("/{client_id}/regenerate-secret", response_model=ApplicationCreateOut)
def regenerate_api_secret(client_id: str, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):
    db_app, api_secret = application_service.regenerate_api_secret(db, client_id)
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    app_data = ApplicationOut.model_validate(db_app).model_dump()
    return ApplicationCreateOut(**app_data, api_secret=api_secret)

@router.get("/", response_model=List[ApplicationOut])
def read_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    return application_service.get_applications(db, skip=skip, limit=limit)

@router.delete("/{app_id}", response_model=dict)
def delete_application(app_id: UUID, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):
    success = application_service.delete_application(db, app_id)
    if not success:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Application successfully revoked"}


