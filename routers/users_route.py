from sqlalchemy.orm import Session
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import users
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

# 모든 사용자 읽기
@router.get("/users", tags=["Users"])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    try:
        users = await db.execute(User.select())
        return users.scalars().all()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

# ID로 사용자 읽기
@router.get("/users/{user_id}", tags=["Users"])
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

# 사용자 생성
@router.post("/users", tags=["Users"])
async def create_user(user: users, db: AsyncSession = Depends(get_db)):
    try:
        new_user = User(login_id=user.login_id, login_pw=user.login_pw, created_at=user.created_at)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

# 사용자 업데이트
@router.put("/users/{user_id}", tags=["Users"])
async def update_user(user_id: int, user: users, db: AsyncSession = Depends(get_db)):
    try:
        existing_user = await db.get(User, user_id)
        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        existing_user.login_id = user.login_id
        existing_user.login_pw = user.login_pw
        existing_user.created_at = user.created_at

        await db.commit()
        await db.refresh(existing_user)
        return existing_user
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

# 사용자 삭제
@router.delete("/users/{user_id}", tags=["Users"])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_user = await db.get(User, user_id)
        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        await db.delete(existing_user)
        await db.commit()

        return {"message": "User deleted"}
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()
    