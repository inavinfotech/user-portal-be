from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import BaseModelMixin, GUID

class UserAddress(Base, BaseModelMixin):
    __tablename__ = "user_addresses"

    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address_line = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)

    user = relationship("User", back_populates="addresses")
