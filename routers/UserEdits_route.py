from models.UserEdits import UserEdit
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import useredits
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/useredits/{user_edit_id}")
async def get_useredit_by_id(user_edit_id: int, db: AsyncSession = Depends(get_db)):
    try:
        useredit = await db.get(UserEdit, user_edit_id)
        if useredit is None:
            raise HTTPException(status_code=404, detail="UserEdit not found")
        return useredit
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/useredits")
async def create_useredit(useredit: useredits, db: AsyncSession = Depends(get_db)):
    try:
        new_useredit = UserEdit(
            user_id = useredit.user_id,
            audio_id = useredit.audio_id,
            result_id = useredit.result_id,
            Effect_Status = useredit.Applied_Effect    
        )
        db.add(new_useredit)
        await db.commit()
        await db.refresh(new_useredit)
        return new_useredit
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.put("/useredits/{user_edit_id}")
async def update_useredit(user_edit_id: int, useredit: useredits, db: AsyncSession = Depends(get_db)):
    try:
        existing_useredit = await db.get(UserEdit, user_edit_id)
        if existing_useredit is None:
            raise HTTPException(status_code=404, detail="UserEdit not found")

        existing_useredit.user_id = useredit.user_id
        existing_useredit.audio_id = useredit.audio_id
        existing_useredit.result_id = useredit.result_id
        existing_useredit.Applied_Effect = useredit.Applied_Effect
        
        await db.commit()
        await db.refresh(existing_useredit)
        return existing_useredit
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.delete("/useredits/{user_edit_id}")
async def delete_useredit(user_edit_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_useredit = await db.get(UserEdit, user_edit_id)
        if existing_useredit is None:
            raise HTTPException(status_code=404, detail="UserEdit not found")

        await db.delete(existing_useredit)
        await db.commit()
        return {"message": "UserEdit deleted"}
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()
