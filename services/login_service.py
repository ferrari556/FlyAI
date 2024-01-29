from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.users import User
import pytz

async def get_user_by_login_id(db: AsyncSession, login_id: str):
    result = await db.execute(select(User).filter_by(login_id=login_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: User):
    existing_user = await get_user_by_login_id(db, user.login_id)
    
    if existing_user:
        raise ValueError("ID Already Registered")
    
    # 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
    korea_time_zone = pytz.timezone("Asia/Seoul")
    created_at_kst = datetime.now(korea_time_zone)
    
    db_user = User(
        login_id=user.login_id,
        login_pw=user.login_pw,
        created_at=created_at_kst
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user