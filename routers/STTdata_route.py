from sqlalchemy.orm import Session
from models.STTdata import STTData
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import STTdata
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

# 모든 STTData 읽기
@router.get("/sttdata", tags=["STTData"])
async def get_all_sttdata(db: Session = Depends(get_db)):
    try:
        sttdata = db.query(STTData).all()
        return sttdata
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

# ID로 STTData 읽기
@router.get("/sttdata/{text_id}", tags=["STTData"])
async def get_sttdata_by_id(text_id: int, db: Session = Depends(get_db)):
    try:
        sttdata = db.query(STTData).filter(STTData.text_id == text_id).first()
        if sttdata is None:
            raise HTTPException(status_code=404, detail="STTData not found")
        return sttdata
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

# 새로운 STTData 생성
@router.post("/sttdata", tags=["STTData"])
async def create_sttdata(sttdata: STTdata, db: Session = Depends(get_db)):
    try:
        new_sttdata = STTData(
            # 스키마에 맞게 필드 할당
        )
        db.add(new_sttdata)
        db.commit()
        db.refresh(new_sttdata)
        return new_sttdata
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

# STTData 업데이트
@router.put("/sttdata/{text_id}", tags=["STTData"])
async def update_sttdata(text_id: int, sttdata: STTdata, db: Session = Depends(get_db)):
    try:
        existing_sttdata = db.query(STTData).filter(STTData.text_id == text_id).first()
        if existing_sttdata is None:
            raise HTTPException(status_code=404, detail="STTData not found")

        # 스키마에 맞게 필드 업데이트

        db.commit()
        db.refresh(existing_sttdata)
        return existing_sttdata
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

# ID로 STTData 삭제
@router.delete("/sttdata/{text_id}", tags=["STTData"])
async def delete_sttdata(text_id: int, db: Session = Depends(get_db)):
    try:
        existing_sttdata = db.query(STTData).filter(STTData.text_id == text_id).first()
        if existing_sttdata is None:
            raise HTTPException(status_code=404, detail="STTData not found")

        db.delete(existing_sttdata)
        db.commit()
        return {"message": "STTData deleted"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()