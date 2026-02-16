from database.connect import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

class StatusFeed(Base):
    __tablename__ = "status_feed"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=True)
    image = Column(String, nullable=True)
    likes_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    hash_tags = Column(ARRAY(String), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    time_posted = Column(TIMESTAMP(timezone=True), default=func.now())

user = relationship("Users")