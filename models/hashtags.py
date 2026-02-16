from database.connect import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship

class HashTags(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False, unique=True, index=True)
    post_count = Column(Integer, default=0)
    time_created = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)