from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List
from uuid import UUID
from app.core.security import get_password_hash, verify_password

class UserService:
    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

    def get_user_by_email(self, db: Session, email: str, include_deleted: bool = False) -> Optional[User]:
        query = db.query(User).filter(User.email == email)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.first()

    def create_user(
        self,
        db: Session,
        user_in: UserCreate,
        created_by_app_id: Optional[UUID] = None,
        creation_source: str = "PORTAL_ADMIN"
    ) -> User:
        existing_user = self.get_user_by_email(db, user_in.email, include_deleted=True)
        if existing_user:
            if not existing_user.is_deleted:
                raise ValueError(f"User with email {user_in.email} already exists")
            
            # Require the correct password to recover soft-deleted account
            if not verify_password(user_in.password, existing_user.hashed_password):
                raise ValueError("An account with this email exists in deactivated state. Correct password is required to recover the account.")

            # Restore soft-deleted user
            existing_user.is_deleted = False
            existing_user.is_active = True
            existing_user.full_name = user_in.full_name
            existing_user.created_by_app_id = created_by_app_id
            existing_user.creation_source = creation_source
            db.add(existing_user)
            db.commit()
            db.refresh(existing_user)
            return existing_user

        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            created_by_app_id=created_by_app_id,
            creation_source=creation_source,
        )
        
        if user_in.roles:
            from app.models.auth import Role
            for role_name in user_in.roles:
                role = db.query(Role).filter(Role.name == role_name).first()
                if role:
                    db_user.roles.append(role)
                    
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


    def update_user(self, db: Session, user_id: UUID, user_in: UserUpdate) -> Optional[User]:
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return None
            
        update_data = user_in.model_dump(exclude_unset=True)
        
        if "email" in update_data and update_data["email"] != db_user.email:
            if self.get_user_by_email(db, update_data["email"]):
                raise ValueError(f"User with email {update_data['email']} already exists")
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            update_data.pop("password")
            
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()

    def delete_user(self, db: Session, user_id: UUID) -> bool:
        db_user = self.get_user_by_id(db, user_id)
        if db_user:
            db_user.is_deleted = True
            db.commit()
            return True
        return False

user_service = UserService()
