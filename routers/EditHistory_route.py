from models.EditHistory import EditHistory, EditText
from models.EditSession import EditSession
from models.Results import Result
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import edithistory
from fastapi.responses import JSONResponse
from config.database import get_db
import pytz
from datetime import datetime

# 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
korea_time_zone = pytz.timezone("Asia/Seoul")
created_at_kst = datetime.now(korea_time_zone)
    
router = APIRouter()

@router.get("/read")
async def get_edithistory_by_id(history_id: int, db: AsyncSession = Depends(get_db)):
    try:
        history = await db.get(EditHistory, history_id)
        if history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")
        return history
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.put("/edit/{history_id}")
async def update_edithistory(history_id: int, edithistory: edithistory, db: AsyncSession = Depends(get_db)):
    try:
        existing_history = await db.get(EditHistory, history_id)
        if existing_history is None:
            raise HTTPException(status_code=404, detail="EditHistory not found")
        
        existing_history.session_id = edithistory.session_id
        existing_history.result_id = edithistory.result_id
        existing_history.Edit_Action = edithistory.Edit_Action
        existing_history.Original_Text = edithistory.Original_Text
        existing_history.Edited_Text = edithistory.Edited_Text
        existing_history.EditDate = edithistory.EditDate

        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()

@router.delete("/delete/{history_id}")
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

router = APIRouter()

@router.post("/edit-text")
async def edit_text(session_id: int, request: EditText, db: AsyncSession = Depends(get_db)):
    result = await db.get(Result, request.result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    new_history = EditHistory(
        session_id=request.session_id,
        result_id=request.result_id,
        audio_id=result.audio_id,
        Edit_Action="Convert Text",
        Original_Text=result.Converted_Result,
        Edited_Text=request.Edited_Text,
        EditDate=created_at_kst
    )

    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)
    
    # 연관된 EditSession 객체 조회
    edit_session = await db.get(EditSession, session_id)
    if not edit_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # EditSession의 last_edit_history_id 업데이트
    edit_session.last_edit_history_id = new_history.history_id
    await db.commit()
    
    return new_history

@router.post("/apply-effect/{result_id}")
async def apply_effect(result_id : int, session_id: int, audio_id : int, db: AsyncSession = Depends(get_db)):
    result = await db.get(Result, result_id)
    
    new_history = EditHistory(
        session_id=session_id,
        result_id=result.result_id,
        audio_id=audio_id,
        Original_Text=result.Converted_Result,
        Edited_Text=result.Converted_Result,
        Edit_Action="Apply Effect",
        EditDate=created_at_kst
    )
    
    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)
    
    # 연관된 EditSession 객체 조회
    edit_session = await db.get(EditSession, session_id)
    if not edit_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # EditSession의 last_edit_history_id 업데이트
    edit_session.last_edit_history_id = new_history.history_id
    await db.commit()
    
    return new_history

@router.post("/cancel-effect/{result_id}")
async def cancel_effect(result_id : int, session_id: int, audio_id : int, db: AsyncSession = Depends(get_db)):
    result = await db.get(Result, result_id)
    
    new_history = EditHistory(
        session_id=session_id,
        result_id=result.result_id,
        audio_id=audio_id,
        Original_Text=result.Converted_Result,
        Edited_Text=result.Converted_Result,
        Edit_Action="Cancel Effect",
        EditDate=created_at_kst
    )
    
    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)
    
    # 연관된 EditSession 객체 조회
    edit_session = await db.get(EditSession, session_id)
    if not edit_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # EditSession의 last_edit_history_id 업데이트
    edit_session.last_edit_history_id = new_history.history_id
    await db.commit()
    
    return new_history