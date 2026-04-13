from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.session import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import user_service
from app.api import deps

router = APIRouter()

@router.post("/", response_model=UserSchema)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    try:
        return user_service.create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    return user_service.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=UserSchema)
def read_user_me(current_user = Depends(deps.get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserSchema)

def read_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: UUID, user_in: UserUpdate, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    try:
        db_user = user_service.update_user(db, user_id, user_in)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
