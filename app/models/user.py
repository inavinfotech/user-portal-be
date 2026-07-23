from sqlalchemy import Column, String, Boolean, ForeignKey, and_
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import BaseModelMixin, GUID
from app.models.auth import user_roles

class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by_app_id = Column(GUID(), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, index=True)
    creation_source = Column(String, default="PORTAL_ADMIN", nullable=False)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("UserAddress", back_populates="user", primaryjoin="and_(User.id==UserAddress.user_id, UserAddress.is_deleted==False)")
    created_by_app = relationship("Application", foreign_keys=[created_by_app_id])

    @property
    def created_by_app_name(self):
        return self.created_by_app.name if self.created_by_app else None


