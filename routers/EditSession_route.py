from sqlalchemy.orm import Session
from models.EditSession import EditSession
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import editsession
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/editsessions/{session_id}")
async def get_editsession_by_id(session_id: int, db: AsyncSession = Depends(get_db)):
    try:
        editsession = await db.get(EditSession, session_id)
        if editsession is None:
            raise HTTPException(status_code=404, detail="EditSession not found")
        return editsession
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/editsessions")
async def create_editsession(editsession: editsession, db: AsyncSession = Depends(get_db)):
    try:
        new_editsession = EditSession(
            user_id=editsession.user_id,
            audio_id=editsession.audio_id,
            effect_id=editsession.effect_id,
            Edit_start=editsession.start_edit,
            Edit_finish=editsession.end_edit,
            LastEditPoint=editsession.LastEditPoint,
        )
        db.add(new_editsession)
        await db.commit()
        await db.refresh(new_editsession)
        return new_editsession
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.put("/editsessions/{session_id}")
async def update_editsession(session_id: int, editsession: editsession, db: AsyncSession = Depends(get_db)):
    try:
        existing_editsession = await db.get(EditSession, session_id)
        if existing_editsession is None:
            raise HTTPException(status_code=404, detail="EditSession not found")

        existing_editsession.user_id = editsession.user_id
        existing_editsession.audio_id = editsession.audio_id
        existing_editsession.effect_id = editsession.effect_id
        existing_editsession.start_edit = editsession.start_edit    
        existing_editsession.end_edit = editsession.end_edit
        existing_editsession.LastEditPoint = editsession.LastEditPoint

        await db.commit()
        await db.refresh(existing_editsession)
        return existing_editsession
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.delete("/editsessions/{session_id}")
async def delete_editsession(session_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_editsession = await db.get(EditSession, session_id)
        if existing_editsession is None:
            raise HTTPException(status_code=404, detail="EditSession not found")

        await db.delete(existing_editsession)
        await db.commit()
        return {"message": "EditSession deleted"}
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()
