from sqlalchemy.orm import Session
from models.UserSoundEffects import UserSoundEffect
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import usersoundeffects
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/usersoundeffects/{id}")
async def get_usersoundeffect_by_id(id: int, db: AsyncSession = Depends(get_db)):
    try:
        usersoundeffect = await db.get(UserSoundEffect, id)
        if usersoundeffect is None:
            raise HTTPException(status_code=404, detail="UserSoundEffect not found")
        return usersoundeffect
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/usersoundeffects")
async def create_usersoundeffect(usersoundeffect: usersoundeffects, db: AsyncSession = Depends(get_db)):
    try:
        new_usersoundeffect = UserSoundEffect(
            user_id = usersoundeffect.user_id,
            effect_id = usersoundeffect.effect_id
        )
        db.add(new_usersoundeffect)
        await db.commit()
        await db.refresh(new_usersoundeffect)
        return new_usersoundeffect
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.put("/usersoundeffects/{id}")
async def update_usersoundeffect(id: int, usersoundeffect: usersoundeffects, db: AsyncSession = Depends(get_db)):
    try:
        existing_usersoundeffect = await db.get(UserSoundEffect, id)
        if existing_usersoundeffect is None:
            raise HTTPException(status_code=404, detail="UserSoundEffect not found")

        existing_usersoundeffect.user_id = usersoundeffect.user_id
        existing_usersoundeffect.effect_id = usersoundeffect.effect_id

        await db.commit()
        await db.refresh(existing_usersoundeffect)
        return existing_usersoundeffect
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.delete("/usersoundeffects/{id}")
async def delete_usersoundeffect(id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_usersoundeffect = await db.get(UserSoundEffect, id)
        if existing_usersoundeffect is None:
            raise HTTPException(status_code=404, detail="UserSoundEffect not found")

        await db.delete(existing_usersoundeffect)
        await db.commit()
        return {"message": "UserSoundEffect deleted"}
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()