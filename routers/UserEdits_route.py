from sqlalchemy.orm import Session
from models.UserEdits import UserEdit
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import UserEdits
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/useredits", tags=["UserEdits"])
async def get_all_useredits(db: Session = Depends(get_db)):
    try:
        useredits = db.query(UserEdit).all()
        return useredits
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.get("/useredits/{user_edit_id}", tags=["UserEdits"])
async def get_useredit_by_id(user_edit_id: int, db: Session = Depends(get_db)):
    try:
        useredit = db.query(UserEdit).filter(UserEdit.user_edit_id == user_edit_id).first()
        if useredit is None:
            raise HTTPException(status_code=404, detail="UserEdit not found")
        return useredit
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/useredits", tags=["UserEdits"])
async def create_useredit(useredit: UserEdits, db: Session = Depends(get_db)):
    try:
        new_useredit = UserEdit(
            # 스키마에 맞게 필드 할당
        )
        db.add(new_useredit)
        db.commit()
        db.refresh(new_useredit)
        return new_useredit
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.put("/useredits/{user_edit_id}", tags=["UserEdits"])
async def update_useredit(user_edit_id: int, useredit: UserEdits, db: Session = Depends(get_db)):
    try:
        existing_useredit = db.query(UserEdit).filter(UserEdit.user_edit_id == user_edit_id).first()
        if existing_useredit is None:
            raise HTTPException(status_code=404, detail="UserEdit not found")

        # 스키마에 맞게 필드 업데이트

        db.commit()
        db.refresh(existing_useredit)
        return existing_useredit
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

@router.delete("/useredits/{user_edit_id}", tags=["UserEdits"])
async def delete_useredit(user_edit_id: int, db: Session = Depends(get_db)):
    try:
        existing_useredit = db.query(UserEdit).filter(UserEdit.user_edit_id == user_edit_id).first()
        if existing_useredit is None:
            raise HTTPException(status_code=404, detail="UserEdit not found")

        db.delete(existing_useredit)
        db.commit()
        return {"message": "UserEdit deleted"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()
