from sqlalchemy.orm import Session
from models.EditHistory import EditHistory
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import EditHistory
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/edithistory", tags=["EditHistory"])
async def get_all_edithistory(db: Session = Depends(get_db)):
    try:
        edithistory = db.query(EditHistory).all()
        return edithistory
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.get("/edithistory/{history_id}", tags=["EditHistory"])
async def get_edithistory_by_id(history_id: int, db: Session = Depends(get_db)):
    try:
        history = db.query(EditHistory).filter(EditHistory.history_id == history_id).first()
        if history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")
        return history
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/edithistory", tags=["EditHistory"])
async def create_edithistory(edithistory: EditHistory, db: Session = Depends(get_db)):
    try:
        new_history = EditHistory(
            # 스키마에 맞게 필드 할당
        )
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        return new_history
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.put("/edithistory/{history_id}", tags=["EditHistory"])
async def update_edithistory(history_id: int, edithistory: EditHistory, db: Session = Depends(get_db)):
    try:
        existing_history = db.query(EditHistory).filter(EditHistory.history_id == history_id).first()
        if existing_history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")

        # 스키마에 맞게 필드 업데이트

        db.commit()
        db.refresh(existing_history)
        return existing_history
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.delete("/edithistory/{history_id}", tags=["EditHistory"])
async def delete_edithistory(history_id: int, db: Session = Depends(get_db)):
    try:
        existing_history = db.query(EditHistory).filter(EditHistory.history_id == history_id).first()
        if existing_history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")

        db.delete(existing_history)
        db.commit()
        return {"message": "EditHistory deleted"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()