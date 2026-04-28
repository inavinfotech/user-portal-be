from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.schemas.address import UserAddress, UserAddressCreate, UserAddressUpdate
from app.services.address_service import address_service
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=UserAddress)
def read_address_me(
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    address = address_service.get_address_by_user_id(db, current_user.id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.post("/me", response_model=UserAddress)
def create_address_me(
    address_in: UserAddressCreate,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    existing = address_service.get_address_by_user_id(db, current_user.id)
    if existing:
        # If exists, update instead of create to ensure only one address per user for now
        update_in = UserAddressUpdate(**address_in.model_dump())
        return address_service.update_address(db, existing.id, update_in)
    
    return address_service.create_address(db, current_user.id, address_in)

@router.put("/me", response_model=UserAddress)
def update_address_me(
    address_in: UserAddressUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    address = address_service.get_address_by_user_id(db, current_user.id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address_service.update_address(db, address.id, address_in)

# External endpoints for the website backend (Proxy)
@router.get("/user/{user_id}", response_model=UserAddress, dependencies=[Depends(deps.verify_api_key)])
def get_user_address_external(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    address = address_service.get_address_by_user_id(db, user_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.post("/user/{user_id}", response_model=UserAddress, dependencies=[Depends(deps.verify_api_key)])
def create_user_address_external(
    user_id: UUID,
    address_in: UserAddressCreate,
    db: Session = Depends(get_db)
):
    existing = address_service.get_address_by_user_id(db, user_id)
    if existing:
        update_in = UserAddressUpdate(**address_in.model_dump())
        return address_service.update_address(db, existing.id, update_in)
    return address_service.create_address(db, user_id, address_in)
