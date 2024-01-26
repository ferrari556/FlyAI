from sqlalchemy.orm import Session
from models.UserSoundEffects import UserSoundEffect
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import UserSoundEffects
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/usersoundeffects", tags=["UserSoundEffects"])
async def get_all_usersoundeffects(db: Session = Depends(get_db)):
    try:
        usersoundeffects = db.query(UserSoundEffect).all()
        return usersoundeffects
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.get("/usersoundeffects/{id}", tags=["UserSoundEffects"])
async def get_usersoundeffect_by_id(id: int, db: Session = Depends(get_db)):
    try:
        usersoundeffect = db.query(UserSoundEffects).filter(UserSoundEffects.id == id).first()
        if usersoundeffect is None:
            raise HTTPException(status_code=404, detail="UserSoundEffect not found")
        return usersoundeffect
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/usersoundeffects", tags=["UserSoundEffects"])
async def create_usersoundeffect(usersoundeffect: UserSoundEffects, db: Session = Depends(get_db)):
    try:
        new_usersoundeffect = UserSoundEffects(
            # 스키마에 맞게 필드 할당
        )
        db.add(new_usersoundeffect)
        db.commit()
        db.refresh(new_usersoundeffect)
        return new_usersoundeffect
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.put("/usersoundeffects/{id}", tags=["UserSoundEffects"])
async def update_usersoundeffect(id: int, usersoundeffect: UserSoundEffects, db: Session = Depends(get_db)):
    try:
        existing_usersoundeffect = db.query(UserSoundEffects).filter(UserSoundEffects.id == id).first()
        if existing_usersoundeffect is None:
            raise HTTPException(status_code=404, detail="UserSoundEffect not found")

        # 스키마에 맞게 필드 업데이트

        db.commit()
        db.refresh(existing_usersoundeffect)
        return existing_usersoundeffect
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.delete("/usersoundeffects/{id}", tags=["UserSoundEffects"])
async def delete_usersoundeffect(id: int, db: Session = Depends(get_db)):
    try:
        existing_usersoundeffect = db.query(UserSoundEffects).filter(UserSoundEffects.id == id).first()
        if existing_usersoundeffect is None:
            raise HTTPException(status_code=404, detail="UserSoundEffect not found")

        db.delete(existing_usersoundeffect)
        db.commit()
        return {"message": "UserSoundEffect deleted"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()