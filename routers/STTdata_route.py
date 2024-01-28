from sqlalchemy.orm import Session
from models.STTdata import STTData
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import sttdata
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/sttdata/{text_id}", tags=["STTData"])
async def get_sttdata_by_id(text_id: int, db: AsyncSession = Depends(get_db)):
    try:
        sttdata = await db.get(STTData, text_id)
        if sttdata is None:
            raise HTTPException(status_code=404, detail="STTData not found")
        return sttdata
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.post("/sttdata", tags=["STTData"])
async def create_sttdata(sttdata: sttdata, db: AsyncSession = Depends(get_db)):
    try:
        new_sttdata = STTData(
            audio_id = sttdata.audio_id,
            Converted_text = sttdata.Converted_text,
            Complete_Convert_Date = sttdata .Complete_Convert_Date   
        )
        db.add(new_sttdata)
        await db.commit()
        await db.refresh(new_sttdata)
        return new_sttdata
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.put("/sttdata/{text_id}", tags=["STTData"])
async def update_sttdata(text_id: int, sttdata: sttdata, db: AsyncSession = Depends(get_db)):
    try:
        existing_sttdata = await db.get(STTData, text_id)
        if existing_sttdata is None:
            raise HTTPException(status_code=404, detail="STTData not found")

        existing_sttdata.audio_id = sttdata.audio_id
        existing_sttdata.Converted_text = sttdata.Converted_text
        existing_sttdata.Complete_Convert_Date = sttdata.Complete_Convert_Date

        await db.commit()
        await db.refresh(existing_sttdata)
        return existing_sttdata
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.delete("/sttdata/{text_id}", tags=["STTData"])
async def delete_sttdata(text_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_sttdata = await db.get(STTData, text_id)
        if existing_sttdata is None:
            raise HTTPException(status_code=404, detail="STTData not found")

        await db.delete(existing_sttdata)
        await db.commit()
        return {"message": "STTData deleted"}
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()