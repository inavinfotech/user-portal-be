from sqlalchemy.orm import Session
from app.models.auth import Role, Permission, user_roles, role_permissions
from app.models.user import User
from app.schemas.auth import RoleCreate, PermissionCreate
from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError

class RBACService:
    def create_role(self, db: Session, role_in: RoleCreate) -> Role:
        db_role = Role(name=role_in.name, description=role_in.description)
        db.add(db_role)
        try:
            db.commit()
            db.refresh(db_role)
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Role with name {role_in.name} already exists")
        return db_role

    def create_permission(self, db: Session, perm_in: PermissionCreate) -> Permission:
        db_perm = Permission(
            name=perm_in.name,
            description=perm_in.description,
            resource=perm_in.resource,
            action=perm_in.action
        )
        db.add(db_perm)
        try:
            db.commit()
            db.refresh(db_perm)
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Permission with name {perm_in.name} already exists")
        return db_perm

    def assign_role_to_user(self, db: Session, user_id: UUID, role_id: UUID):
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()
        if not user or not role:
            raise ValueError("User or Role not found")
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
        return user

    def assign_permission_to_role(self, db: Session, role_id: UUID, permission_id: UUID):
        role = db.query(Role).filter(Role.id == role_id).first()
        perm = db.query(Permission).filter(Permission.id == permission_id).first()
        if not role or not perm:
            raise ValueError("Role or Permission not found")
        
        if perm not in role.permissions:
            role.permissions.append(perm)
            db.commit()
        return role

    def get_roles(self, db: Session) -> List[Role]:
        return db.query(Role).all()

    def get_permissions(self, db: Session) -> List[Permission]:
        return db.query(Permission).all()

rbac_service = RBACService()
