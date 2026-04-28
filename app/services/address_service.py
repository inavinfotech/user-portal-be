from sqlalchemy.orm import Session
from app.models.address import UserAddress
from app.schemas.address import UserAddressCreate, UserAddressUpdate
from uuid import UUID

class AddressService:
    def get_address_by_user_id(self, db: Session, user_id: UUID):
        return db.query(UserAddress).filter(UserAddress.user_id == user_id, UserAddress.is_deleted == False).first()

    def create_address(self, db: Session, user_id: UUID, address_in: UserAddressCreate):
        db_address = UserAddress(
            user_id=user_id,
            **address_in.model_dump()
        )
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        return db_address

    def update_address(self, db: Session, address_id: UUID, address_in: UserAddressUpdate):
        db_address = db.query(UserAddress).filter(UserAddress.id == address_id).first()
        if not db_address:
            return None
        
        update_data = address_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_address, field, value)
        
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        return db_address

address_service = AddressService()
