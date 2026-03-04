from datetime import datetime, timedelta, timezone
from gc import get_count
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import SessionLocal
class CountCRUD:
    def __init__(self):
        pass

    async def get_count(self, model, compare: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
        async with SessionLocal() as db:
            count = select(func.count()).select_from(model)

            if start_date and end_date:
                count = count.where(compare >= start_date, compare < end_date)
            count = await db.execute(count)
            total_counts = count.scalar_one()

            return total_counts
        
    async def get_statistics(self, model, compare):
        async with SessionLocal() as db:
            # 1. Define your date range (Today at midnight, and 6 days prior to make 7 days total)
            today = datetime.now(timezone.utc).date()
            seven_days_ago = today - timedelta(days=6)

            # Define expressions as variables for clean reuse
            truncated_date = func.date_trunc('day', compare)
            day_name = func.to_char(truncated_date, 'Dy')
            
            stmt = (
                select(
                    day_name.label("day"), 
                    truncated_date.label("date"), 
                    func.count().label("count")
                )
                .select_from(model)
                .where(compare >= seven_days_ago)
                .group_by(
                    truncated_date, 
                    day_name  # <-- Added to satisfy PostgreSQL
                )
            )
            
            result = await db.execute(stmt)
            fetched_data = result.all()
            
            # 3. Use .date() in the dictionary key to ensure the match is "Day-to-Day"
            db_counts = {row.date.date(): row.count for row in fetched_data}

            # 4. Generate the flawless 7-day continuous list
            final_statistics = []
            
            # Loop from 6 days ago down to 0 (today)
            for i in range(6, -1, -1): 
                current_date = seven_days_ago + timedelta(days=i)
                
                final_statistics.append({
                    "day": current_date.strftime("%a"), # e.g., 'Mon', 'Tue'
                    "date": current_date,
                    "count": db_counts.get(current_date, 0) # Fetch the count, or default to 0
                })
                
            return final_statistics