from database.connect import Base
from sqlalchemy import Column, String, Boolean, Integer, DateTime, func, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

class Tokens(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(255), nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    expiry = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    anonyuser = relationship("Users")