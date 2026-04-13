from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class SessionBase(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class Session(SessionBase):
    id: UUID
    token_jti: str
    expires_at: datetime
    created_at: datetime
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)

class SessionRevoke(BaseModel):
    token_jti: str
