from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import BaseModelMixin, GUID

# Association Tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", GUID(), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base, BaseModelMixin):
    __tablename__ = "roles"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base, BaseModelMixin):
    __tablename__ = "permissions"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    resource = Column(String, index=True) # e.g., 'users', 'roles'
    action = Column(String) # e.g., 'read', 'write', 'delete'

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
