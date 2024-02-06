from models.EditSession import EditSession, SessionUpdate, SessionCreate, SessionResponse, SessionPause, SessionRead
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
@router.get("/read", response_model=SessionResponse)
async def get_session(user_id: int, session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.execute(
        select(EditSession).filter_by(user_id=user_id, session_id=session_id)
    )
    session_data = session.scalars().first()
    if session_data:
        return session_data
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# # 세션 시작
# @router.post("/start-session", response_model=SessionResponse)
# async def start_session(request: Request, token: str = Depends(oauth2_scheme),session_start_request: SessionCreate = Body(...), db: AsyncSession = Depends(get_db)):
    
#     login_id = await get_current_user_authorization(request, token)
#     user_id = await get_user_id_by_login_id(db, login_id)
#     if user_id is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     audio_id = session_start_request.audio_id 
#     if audio_id is None:
#         raise HTTPException(status_code=404, detail="Audio not found")
     
#     # 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
#     korea_time_zone = pytz.timezone("Asia/Seoul")
#     created_at_kst = datetime.now(korea_time_zone)
    
#     session = EditSession(
#         user_id=user_id,
#         audio_id=audio_id,
#         Start_Edit=created_at_kst,
#         Session_State="Active"
#     )
    
#     db.add(session)
#     await db.commit()
#     return session
@router.post("/start", response_model=SessionResponse)
async def start_session(request: Request, token: str = Depends(oauth2_scheme), session_start_request: SessionCreate = Body(...), db: AsyncSession = Depends(get_db)):
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

    # 세션 객체 생성
    session = EditSession(
        user_id=user_id,
        audio_id=audio_id,
        Start_Edit=created_at_kst,
        Session_State="Active"
    )

    db.add(session)
    await db.commit()

    # EditHistory 객체 생성
    edit_history = EditHistory(
        session_id=session.session_id,
        audio_id=audio_id,
        result_id=None,  # 세션 시작 시점에서는 result_id를 알 수 없으므로 None으로 설정
        Edit_Action="Session Start",
        Original_Text="Empty",  # 세션 시작에는 원본 텍스트가 없으므로 비워둠
        Edited_Text="Empty",  # 세션 시작에는 편집된 텍스트가 없으므로 비워둠
        EditDate=created_at_kst,
    )

    db.add(edit_history)
    await db.commit()

    # 세션 정보를 반환하기 전에 EditHistory 정보 업데이트
    session.last_edit_history_id = edit_history.history_id
    await db.commit()

    return session

# 세션 중단, 마지막 편집점 기록
@router.patch("/pause/{session_id}", response_model=SessionPause)
async def update_session(session_id: int, update_data: SessionUpdate, db: AsyncSession = Depends(get_db)):
    session = await db.get(EditSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found") 
    
    session.Session_State="Pause"
    
    await db.commit()
    return session

# # 세션 중단 (Pause)
# @router.patch("/session/pause/{session_id}", response_model=SessionUpdate)
# async def pause_session(session_id: int, edit_data: EditHistoryCreate, db: AsyncSession = Depends(get_db)):
#     session = await db.get(EditSession, session_id)
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found")

#     # 마지막 편집 이력을 EditHistory에 기록
#     new_history = EditHistory(**edit_data.dict(), edit_date=datetime.utcnow())
#     db.add(new_history)
#     await db.commit()
#     await db.refresh(new_history)

#     # 마지막 편집 이력 ID를 세션에 기록
#     session.last_edit_history_id = new_history.history_id
#     session.Session_State = "Pause"
#     await db.commit()

#     return {"message": "Session paused", "last_edit_history_id": new_history.history_id}

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

    # 마지막 편집 상태 복원 로직
    last_edit_history_id = session.last_edit_history_id
    if last_edit_history_id:
        # EditHistory 및 관련 Result 정보 로드
        last_edit_history = await db.get(EditHistory, last_edit_history_id)
        if last_edit_history:
            last_result = await db.get(Result, last_edit_history.result_id)
            
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

            korea_time_zone = pytz.timezone("Asia/Seoul")
            created_at_kst = datetime.now(korea_time_zone)
            
            session.Session_State = "Active"
            session.Start_Edit = created_at_kst  # 현재 시간으로 다시 시작 지점을 업데이트   
            await db.commit()
            
            # 클라이언트에 필요한 정보를 포함하는 응답 반환
            return response_data
        else:
            raise HTTPException(status_code=404, detail="Last edit history not found")
    else:
        # last_edit_history_id가 없는 경우의 처리 로직
        raise HTTPException(status_code=404, detail="Last edit history not found")