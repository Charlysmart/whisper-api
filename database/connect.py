from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from config.setting import Setting

setting = Setting()
engine = create_async_engine(url=setting.databaseurl, echo=True)

SessionLocal = async_sessionmaker(
    class_= AsyncSession,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()