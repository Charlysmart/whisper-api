from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE:str
engine = create_async_engine(url=DATABASE, echo=True)

SessionLocal = async_sessionmaker(
    class_= AsyncSession,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()