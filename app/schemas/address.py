from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserAddressBase(BaseModel):
    full_name: str
    phone_number: str
    address_line: str
    city: str
    state: str
    postal_code: str

class UserAddressCreate(UserAddressBase):
    pass

class UserAddressUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None

class UserAddress(UserAddressBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
