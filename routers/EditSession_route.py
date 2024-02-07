from models.EditSession import EditSession, SessionCreate, SessionResponse, SessionPause
from models.Results import Result
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from config.database import get_db
from sqlalchemy.future import select
import pytz
from datetime import datetime
from services.Login_Service import oauth2_scheme, get_current_user_authorization
from services.AudioFiles_service import get_user_id_by_login_id
from services.EditSession_service import (
    start_session, 
    pause_session, 
    end_session, 
    resume_session,
    get_session)

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
    
@router.post("/start", response_model=SessionResponse)
async def start(request: Request, token: str = Depends(oauth2_scheme), session_start_request: SessionCreate = Body(...), db: AsyncSession = Depends(get_db)):
    login_id = await get_current_user_authorization(request, token)
    user_id = await get_user_id_by_login_id(db, login_id)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    session = await start_session(db, user_id, session_start_request.audio_id)
    return session

@router.patch("/pause/{session_id}", response_model=SessionPause)
async def pause(session_id: int, db: AsyncSession = Depends(get_db)):
    return await pause_session(db, session_id)

@router.post("/end/{session_id}", response_model=SessionResponse)
async def end(session_id: int, db: AsyncSession = Depends(get_db)):
    return await end_session(db, session_id)

@router.patch("/resume/{session_id}", response_model=SessionResponse)
async def resume(session_id: int, db: AsyncSession = Depends(get_db)):
    try:
        response_data = await resume_session(db, session_id)
        return response_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    