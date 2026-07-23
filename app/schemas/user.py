from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.address import UserAddress

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    roles: Optional[List[str]] = None

class UserUpdate(UserBase):
    password: Optional[str] = None

# Role schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class Role(RoleBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    created_by_app_id: Optional[UUID] = None
    created_by_app_name: Optional[str] = None
    creation_source: Optional[str] = "PORTAL_ADMIN"
    roles: List[Role] = []
    addresses: List[UserAddress] = []

    model_config = ConfigDict(from_attributes=True)


