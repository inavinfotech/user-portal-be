from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class ApplicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Application(ApplicationBase):
    id: UUID
    client_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApplicationOut(ApplicationBase):
    id: UUID
    client_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ApplicationCreateOut(ApplicationOut):
    api_secret: str
