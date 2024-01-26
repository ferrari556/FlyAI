from sqlalchemy.orm import Session
from models.Effectsounds import EffectSound
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import Effectsounds
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/effectsounds", tags=["EffectSounds"])
async def get_all_effectsounds(db: Session = Depends(get_db)):
    try:
        effectsounds = db.query(EffectSound).all()
        return effectsounds
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.get("/effectsounds/{effect_id}", tags=["EffectSounds"])
async def get_effectsound_by_id(effect_id: int, db: Session = Depends(get_db)):
    try:
        effectsound = db.query(Effectsounds).filter(Effectsounds.effect_id == effect_id).first()
        if effectsound is None:
            raise HTTPException(status_code=404, detail="EffectSound not found")
        return effectsound
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/effectsounds", tags=["EffectSounds"])
async def create_effectsound(effectsound: Effectsounds, db: Session = Depends(get_db)):
    try:
        new_effectsound = Effectsounds(
            # 스키마에 맞게 필드 할당
        )
        db.add(new_effectsound)
        db.commit()
        db.refresh(new_effectsound)
        return new_effectsound
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.put("/effectsounds/{effect_id}", tags=["EffectSounds"])
async def update_effectsound(effect_id: int, effectsound: Effectsounds, db: Session = Depends(get_db)):
    try:
        existing_effectsound = db.query(Effectsounds).filter(Effectsounds.effect_id == effect_id).first()
        if existing_effectsound is None:
            raise HTTPException(status_code=404, detail="EffectSound not found")

        # 스키마에 맞게 필드 업데이트

        db.commit()
        db.refresh(existing_effectsound)
        return existing_effectsound
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.delete("/effectsounds/{effect_id}", tags=["EffectSounds"])
async def delete_effectsound(effect_id: int, db: Session = Depends(get_db)):
    try:
        existing_effectsound = db.query(Effectsounds).filter(Effectsounds.effect_id == effect_id).first()
        if existing_effectsound is None:
            raise HTTPException(status_code=404, detail="EffectSound not found")

        db.delete(existing_effectsound)
        db.commit()
        return {"message": "EffectSound deleted"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()
