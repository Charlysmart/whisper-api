from database.connect import SessionLocal

async def get_db():
    async with SessionLocal() as session:
        yield session