from database.connect import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, ForeignKey

class Room(Base):
    __tablename__ = "whisperroom"

    id = Column(Integer, primary_key=True)
    room_name = Column(String, nullable=False)
    room_thread = Column(String, nullable=False, unique=True, index=True)
    admin = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    display_admin = Column(Boolean, nullable=False, default=False)
    time_created = Column(TIMESTAMP(timezone=True), server_default=func.now())