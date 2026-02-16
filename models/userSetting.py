from database.connect import Base
from sqlalchemy import Column, BOOLEAN, func, TIMESTAMP, INTEGER, ForeignKey
from sqlalchemy.orm import relationship

class UserSetting(Base):
    __tablename__ = "user_preference"

    id = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    email = Column(BOOLEAN, default=False, nullable=False)
    push = Column(BOOLEAN, default=False, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now())


user = relationship("Users")