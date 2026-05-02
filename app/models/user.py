from sqlalchemy import Column, String, Boolean, and_
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import BaseModelMixin
from app.models.auth import user_roles

class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("UserAddress", back_populates="user", primaryjoin="and_(User.id==UserAddress.user_id, UserAddress.is_deleted==False)")
