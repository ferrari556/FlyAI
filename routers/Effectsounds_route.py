from sqlalchemy.orm import Session
from models.Effectsounds import EffectSound
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import effectsounds
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/effectsounds/{effect_id}", tags=["EffectSounds"])
async def get_effectsound_by_id(effect_id: int, db: AsyncSession = Depends(get_db)):
    try:
        effectsound = await db.get(EffectSound, effect_id)
        if effectsound is None:
            raise HTTPException(status_code=404, detail="EffectSound not found")
        return effectsound
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/effectsounds", tags=["EffectSounds"])
async def create_effectsound(effectsound: effectsounds, db: AsyncSession = Depends(get_db)):
    try:
        new_effectsound = EffectSound(
            effect_name = effectsound.effect_name,
            Effect_Path = effectsound.Effect_Path,
            Effect_Length = effectsound.Effect_Length,
            Effect_number = effectsound.Effect_number
        )
        
        db.add(new_effectsound)
        await db.commit()
        await db.refresh(new_effectsound)
        return new_effectsound
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.put("/effectsounds/{effect_id}", tags=["EffectSounds"])
async def update_effectsound(effect_id: int, effectsound: effectsounds, db: AsyncSession = Depends(get_db)):
    try:
        existing_effectsound = await db.get(EffectSound, effect_id)
        if existing_effectsound is None:
            raise HTTPException(status_code=404, detail="EffectSound not found")

        existing_effectsound.effect_name = effectsound.effect_name
        existing_effectsound.Effect_Path = effectsound.Effect_Path
        existing_effectsound.Effect_Length = effectsound.Effect_Length
        existing_effectsound.Effect_number = effectsound.Effect_number

        await db.commit()
        await db.refresh(existing_effectsound)
        return existing_effectsound
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.delete("/effectsounds/{effect_id}", tags=["EffectSounds"])
async def delete_effectsound(effect_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_effectsound = await db.get(EffectSound, effect_id)
        if existing_effectsound is None:
            raise HTTPException(status_code=404, detail="EffectSound not found")

        await db.delete(existing_effectsound)
        await db.commit()
        return {"message": "EffectSound deleted"}
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()
