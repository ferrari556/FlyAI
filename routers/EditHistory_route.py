from sqlalchemy.orm import Session
from models.EditHistory import EditHistory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import edithistory
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/edithistory/{history_id}")
async def get_edithistory_by_id(history_id: int, db: AsyncSession = Depends(get_db)):
    try:
        history = await db.get(EditHistory, history_id)
        if history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")
        return history
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/edithistory")
async def create_edithistory(edithistory: edithistory, db: AsyncSession = Depends(get_db)):
    try:
        new_history = EditHistory(
            session_id=edithistory.session_id,
            user_id=edithistory.user_id,
            ChangeContent=edithistory.EditContent,
            ChangeTime=edithistory.EditDate
        )
        db.add(new_history)
        await db.commit()
        await db.refresh(new_history)
        return new_history
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.put("/edithistory/{history_id}")
async def update_edithistory(history_id: int, edithistory: edithistory, db: AsyncSession = Depends(get_db)):
    try:
        existing_history = await db.get(EditHistory, history_id)
        if existing_history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")
        
        existing_history.session_id = edithistory.session_id
        existing_history.user_id = edithistory.user_id
        existing_history.EditContent = edithistory.EditContent
        existing_history.EditDate = edithistory.EditDate

        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.delete("/edithistory/{history_id}")
async def delete_edithistory(history_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_history = await db.get(EditHistory, history_id)
        if existing_history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")

        await db.delete(existing_history)
        await db.commit()
        return {"message": "EditHistory deleted"}
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()