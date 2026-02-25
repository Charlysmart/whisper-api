from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from database.connect import Base


class BlockChat(Base):
    __tablename__ = "block_chat"

    id = Column(Integer, primary_key=True)
    thread = Column(String, ForeignKey("anonymous.message_thread", ondelete="CASCADE"), nullable=False, index=True)
    blocked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_stamp = Column(TIMESTAMP(timezone=True), server_default=func.now())