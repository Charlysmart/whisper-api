from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, func
from database.connect import Base

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    message_thread = Column(String(255), ForeignKey("anonymous.message_thread"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=True)
    image = Column(String, nullable=True)
    read = Column(Boolean, default=False, nullable=False)
    reply_to = Column(Integer, ForeignKey("chat.id"))
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())