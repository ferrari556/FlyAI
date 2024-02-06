from models.EditSession import EditSession
from models.EditHistory import EditHistory
from models.Results import Result
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import pytz
from datetime import datetime

korea_time_zone = pytz.timezone("Asia/Seoul")
created_at_kst = datetime.now(korea_time_zone)

# 세션 조회
async def get_session(user_id: int, session_id: int, db: AsyncSession):
    session = await db.execute(
        select(EditSession).filter_by(user_id=user_id, session_id=session_id)
    )
    session_data = session.scalars().first()

    if session_data:
        return session_data
    else:
        raise ValueError("Session not found")
    
# 세션 생성
async def start_session(db: AsyncSession, user_id: int, audio_id: int):

    session = EditSession(
        user_id=user_id,
        audio_id=audio_id,
        Start_Edit=created_at_kst,
        Session_State="Active"
    )

    db.add(session)
    await db.commit()

    edit_history = EditHistory(
        session_id=session.session_id,
        audio_id=audio_id,
        Edit_Action="Session Start",
        Original_Text="Empty",
        Edited_Text="Empty",
        EditDate=created_at_kst,
    )

    db.add(edit_history)
    await db.commit()

    session.last_edit_history_id = edit_history.history_id
    await db.commit()

    return session

# 세션 중단
async def pause_session(db: AsyncSession, session_id: int):
    session = await db.get(EditSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.End_Edit = created_at_kst
    session.Session_State = "Pause"
    await db.commit()
    return session

async def end_session(db: AsyncSession, session_id: int):
    session = await db.get(EditSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.End_Edit = created_at_kst
    session.Session_State = "End"
    await db.commit()
    return {"message": "Session Ended"}

async def resume_session(db: AsyncSession, session_id: int):
    session = await db.get(EditSession, session_id)
    if not session:
        raise ValueError("Session not found")

    if session.last_edit_history_id:
        last_edit_history = await db.get(EditHistory, session.last_edit_history_id)
        if not last_edit_history:
            raise HTTPException(status_code=404, detail="Last edit history not found")

        last_result = await db.get(Result, last_edit_history.result_id)
        if not last_result:
            raise HTTPException(status_code=404, detail="Result not found")

        # 복원된 편집 상태 정보를 포함한 응답을 반환합니다.
        response_data = {
            "message": "Session Resumed",
            
            "last_edit_history": {
                "history_id": last_edit_history.history_id,
                "edit_action": last_edit_history.Edit_Action,
                "original_text": last_edit_history.Original_Text,
                "edited_text": last_edit_history.Edited_Text,
                "edit_date": last_edit_history.EditDate
            },
            "last_result": {
                "result_id": last_result.result_id,
                "converted_result": last_result.Converted_Result,
                "is_text": last_result.Is_Text,
                "effect_file_path": last_result.EffectFilePath,
                "converted_date": last_result.Converted_Date
            }
        }

        # 세션 상태 업데이트
        session.Session_State = "Active"
        session.Start_Edit = created_at_kst  # 현재 시간으로 다시 시작 지점을 업데이트 
        # 현재 시간으로 업데이트
        await db.commit()
        return response_data 
    else:
        raise ValueError("Last edit history not found")
