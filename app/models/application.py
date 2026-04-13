from sqlalchemy import Column, String, Boolean
from app.db.session import Base
from app.models.base import BaseModelMixin

class Application(Base, BaseModelMixin):
    __tablename__ = "applications"

    name = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(String, unique=True, index=True, nullable=False)
    api_secret_hash = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)

