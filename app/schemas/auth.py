from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: UUID
    permissions: List[Permission] = []
    model_config = ConfigDict(from_attributes=True)

class RoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID

class PermissionAssignment(BaseModel):
    role_id: UUID
    permission_id: UUID
