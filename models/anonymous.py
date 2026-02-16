from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, func
from database.connect import Base

class Anonymous(Base):
    __tablename__ = "anonymous"

    id = Column(Integer, primary_key=True)
    message_thread = Column(String(255), unique=True, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    be_replied = Column(Boolean, default=True)
    replied = Column(Boolean, default=False)
    read = Column(Boolean, default=False)
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())