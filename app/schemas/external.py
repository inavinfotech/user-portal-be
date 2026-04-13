from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from app.schemas.user import User as UserSchema
from app.schemas.auth import Permission

class ExternalUserResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    roles: List[str]

    model_config = ConfigDict(from_attributes=True)

class TokenValidationResponse(BaseModel):
    is_valid: bool
    user_id: Optional[UUID] = None
    session_id: Optional[str] = None
    expires_at: Optional[float] = None

class PermissionResponse(BaseModel):
    user_id: UUID
    permissions: List[Permission]

    model_config = ConfigDict(from_attributes=True)
