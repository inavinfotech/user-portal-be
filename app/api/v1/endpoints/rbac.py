from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.auth import (
    Role, RoleCreate, RoleAssignment,
    Permission, PermissionCreate, PermissionAssignment
)
from app.services.rbac_service import rbac_service
from app.api import deps

router = APIRouter()

@router.post("/roles", response_model=Role)
def create_role(role_in: RoleCreate, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    # In a real app, only admins should do this. For now, any authenticated user for testing.
    try:
        return rbac_service.create_role(db, role_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/permissions", response_model=Permission)
def create_permission(perm_in: PermissionCreate, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    try:
        return rbac_service.create_permission(db, perm_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assignments/user-role")
def assign_role_to_user(assignment: RoleAssignment, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    try:
        rbac_service.assign_role_to_user(db, assignment.user_id, assignment.role_id)
        return {"detail": "Role assigned successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assignments/role-permission")
def assign_permission_to_role(assignment: PermissionAssignment, db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    try:
        rbac_service.assign_permission_to_role(db, assignment.role_id, assignment.permission_id)
        return {"detail": "Permission assigned successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/roles", response_model=List[Role])
def read_roles(db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    return rbac_service.get_roles(db)

@router.get("/permissions", response_model=List[Permission])
def read_permissions(db: Session = Depends(get_db), current_admin = Depends(deps.RoleChecker(["admin"]))):

    return rbac_service.get_permissions(db)

