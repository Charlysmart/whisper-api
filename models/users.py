from sqlalchemy import Column, String, Boolean, Integer, DateTime, func
from database.connect import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False, unique=True)
    custom_username = Column(String(50), nullable=False, unique=True)
    anony_username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())