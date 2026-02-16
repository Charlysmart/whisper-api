from database.connect import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, ForeignKey

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    content = Column(String, nullable=True)
    read = Column(Boolean, nullable=False, default=False)
    notify_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    added = Column(TIMESTAMP(timezone=True), default=func.now())