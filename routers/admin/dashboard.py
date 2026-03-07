import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from database.session import get_db
from models.anonymous import Anonymous
from models.users import Users
from routers.admin.user_management import UserCrud
from services.count import CountCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from utils.oauth import RoleChecker


dashboard_router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])
countCrud = CountCRUD()

@dashboard_router.get("/dashboard")
async def dashboard(admin: dict = Depends(RoleChecker()), db: AsyncSession = Depends(get_db)):
    # Overview Statistics

    start_day = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    end_day = start_day + timedelta(days=1)
    total_users, total_anonymous, new_users, new_anonymous = await asyncio.gather(
        countCrud.get_count(Users),
        countCrud.get_count(Anonymous),
        countCrud.get_count(Users, compare=Users.created_at, start_date=start_day, end_date=end_day),
        countCrud.get_count(Anonymous, compare=Anonymous.sent_at, start_date=start_day, end_date=end_day)
    )


    # Recent Users
    recent_users = await UserCrud.get_all_specified_users(db, 5, "desc", None, **{"role" : "user"})
    recent = []
    
    if recent_users and recent_users.get("result"):
        recent = [
            {
                "custom_username": u.custom_username,
                "time_joined": u.created_at
            }
            for u in recent_users["result"]
        ]

    # Chart statsitics
    new_signups = await countCrud.get_statistics(Users, Users.created_at)
    new_messages = await countCrud.get_statistics(Anonymous, Anonymous.sent_at)

    # Ensure charts always return arrays
    new_signups = new_signups or []
    new_messages = new_messages or []

    return {
        "statistics" : {
            "total_users" : total_users or 0,
            "total_anonymous" : total_anonymous or 0,
            "new_users" : new_users or 0,
            "new_anonymous" : new_anonymous or 0,
        },
        "recent_users" : recent,
        "chart_stat" : {
            "new_signups" : new_signups,
            "new_messages" : new_messages
        }
    }