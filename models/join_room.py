from database.connect import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey

class JoinRoom(Base):
    __tablename__ = "joined_room_users"

    id = Column(Integer, primary_key=True)
    room_thread = Column(String, ForeignKey("whisperroom.room_thread", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(TIMESTAMP(timezone=True), server_default=func.now())