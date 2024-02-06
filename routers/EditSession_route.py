from models.EditSession import EditSession, SessionUpdate, SessionCreate, SessionResponse, SessionPause
from models.Results import Result
from models.EditHistory import EditHistory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from config.database import get_db
from sqlalchemy.future import select
import pytz
from datetime import datetime
from services.login_service import oauth2_scheme, get_current_user_authorization
from services.audio_service import get_user_id_by_login_id

router = APIRouter()

# 세션 읽기
@router.get("/read/{user_id}")
async def list_sessions(user_id: int, db: AsyncSession = Depends(get_db)):
    sessions = await db.execute(select(EditSession).filter(EditSession.user_id == user_id))
    return sessions.scalars().all()

# 세션 시작
@router.post("/start", response_model=SessionResponse)
async def start_session(request: Request, token: str = Depends(oauth2_scheme),session_start_request: SessionCreate = Body(...), db: AsyncSession = Depends(get_db)):
    
    login_id = await get_current_user_authorization(request, token)
    user_id = await get_user_id_by_login_id(db, login_id)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    audio_id = session_start_request.audio_id 
    if audio_id is None:
        raise HTTPException(status_code=404, detail="Audio not found")
     
    # 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
    korea_time_zone = pytz.timezone("Asia/Seoul")
    created_at_kst = datetime.now(korea_time_zone)
    
    session = EditSession(
        user_id=user_id,
        audio_id=audio_id,
        Start_Edit=created_at_kst,
        Session_State="Active"
    )
    
    db.add(session)
    await db.commit()
    return session

# 세션 중단, 마지막 편집점 기록
@router.patch("/pause/{session_id}", response_model=SessionPause)
async def update_session(session_id: int, update_data: SessionUpdate, db: AsyncSession = Depends(get_db)):
    session = await db.get(EditSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found") 
    
    session.last_edit_history=update_data.last_edit_history
    session.Session_State="Pause"
    
    await db.commit()
    return session

# 세션 완료
@router.post("/end/{session_id}")
async def end_session(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.get(EditSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
    korea_time_zone = pytz.timezone("Asia/Seoul")
    created_at_kst = datetime.now(korea_time_zone)
    
    session.End_Edit = created_at_kst
    session.Session_State = "End"

    await db.commit()
    return {"message": "Session Ended"}

# 세션 재개
@router.patch("/resume/{session_id}")
async def resume_session(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.get(EditSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    last_edit_history = await db.get(EditHistory, session.last_edit_history_id)
    if not last_edit_history:
        raise HTTPException(status_code=404, detail="Last edit history not found")

    last_result = await db.get(Result, last_edit_history.result_id)
    if not last_result:
        raise HTTPException(status_code=404, detail="Last result not found")
    
    korea_time_zone = pytz.timezone("Asia/Seoul")
    created_at_kst = datetime.now(korea_time_zone)
    
    session.Session_State = "Active"
    session.Start_Edit = created_at_kst  # 현재 시간으로 다시 시작 지점을 업데이트    
    await db.commit()
    
    # 복원된 편집 상태 정보를 포함한 응답을 반환합니다.
    # 여기서는 간단한 예시로, 실제 응답에는 클라이언트가 필요로 하는 상세 정보를 포함시켜야 합니다.
    return {
        "message": "Session resumed",
        
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

