from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.notification import Notification
from schemas.notification import Filter

class NotificationCRUD:
    def __init__(self):
        pass

    async def add_notification(self, db: AsyncSession, **info):
        notify = await Notification(**info)
        db.add(notify)

        try:
            await db.commit()
            await db.refresh(notify)
        except:
            await db.rollback()
            return False
        return notify
    
    async def get_notification(self, db: AsyncSession, filter: Filter, page: int, user_id: int):
        limit = 10
        skip = (page - 1) * limit

        stmt = select(Notification).where(Notification.user_id == user_id)
        if filter == "unread":
            stmt = stmt.where(Notification.read == False)
        stmt = await db.execute(stmt.order_by(Notification.added.desc()).offset(skip).limit(limit))            
        result = stmt.scalars().all()

        notify = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        if filter == "unread":
            notify = notify.where(Notification.read == False)
        notify = await db.execute(notify)
        notify_count = notify.scalar_one()

        if result and notify_count:
            return {
                "notification" : result,
                "notify_count" : notify_count
            }
        return False