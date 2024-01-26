from sqlalchemy.orm import Session
from models.EditSession import EditSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import EditSession
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/editsessions", tags=["EditSessions"])
async def get_all_editsessions(db: Session = Depends(get_db)):
    try:
        editsessions = db.query(EditSession).all()
        return editsessions
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.get("/editsessions/{session_id}", tags=["EditSessions"])
async def get_editsession_by_id(session_id: int, db: Session = Depends(get_db)):
    try:
        editsession = db.query(EditSession).filter(EditSession.session_id == session_id).first()
        if editsession is None:
            raise HTTPException(status_code=404, detail="EditSession not found")
        return editsession
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/editsessions", tags=["EditSessions"])
async def create_editsession(editsession: EditSession, db: Session = Depends(get_db)):
    try:
        new_editsession = EditSession(
            # 스키마에 맞게 필드 할당
        )
        db.add(new_editsession)
        db.commit()
        db.refresh(new_editsession)
        return new_editsession
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.put("/editsessions/{session_id}", tags=["EditSessions"])
async def update_editsession(session_id: int, editsession: EditSession, db: Session = Depends(get_db)):
    try:
        existing_editsession = db.query(EditSession).filter(EditSession.session_id == session_id).first()
        if existing_editsession is None:
            raise HTTPException(status_code=404, detail="EditSession not found")

        # 스키마에 맞게 필드 업데이트

        db.commit()
        db.refresh(existing_editsession)
        return existing_editsession
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.delete("/editsessions/{session_id}", tags=["EditSessions"])
async def delete_editsession(session_id: int, db: Session = Depends(get_db)):
    try:
        existing_editsession = db.query(EditSession).filter(EditSession.session_id == session_id).first()
        if existing_editsession is None:
            raise HTTPException(status_code=404, detail="EditSession not found")

        db.delete(existing_editsession)
        db.commit()
        return {"message": "EditSession deleted"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()