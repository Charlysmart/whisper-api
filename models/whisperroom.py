from database.connect import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship

class Whisperroom(Base):
    __tablename__ = "whisperroom_chat"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=True)
    image = Column(String, nullable=True)
    reply_to = Column(Integer, ForeignKey("whisperroom_chat.id"))
    room_thread = Column(String, ForeignKey("whisperroom.room_thread", ondelete="CASCADE"))
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

user = relationship("Room")