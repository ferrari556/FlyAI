from models.EditSession import EditSession
from models.EditHistory import EditHistory
from models.EffectSounds import EffectSound
from models.Results import Result
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import pytz
from datetime import datetime

korea_time_zone = pytz.timezone("Asia/Seoul")
created_at_kst = datetime.now(korea_time_zone)

# 세션 조회
async def get_session(db: AsyncSession, session_id: int):
    session = await db.execute(
        select(EditSession).filter_by(session_id=session_id)
    )
    session_data = session.scalars().first()

    if session_data:
        return session_data
    else:
        raise ValueError("Session not found")
    
# 세션 생성 함수
async def start_session(db: AsyncSession, user_id: int, audio_id: int):
    created_at_kst = datetime.now(korea_time_zone)
    
    # EditSession 테이블에 새로운 세션 정보 생성
    new_session = EditSession(
        user_id=user_id,
        audio_id=audio_id,
        Start_Edit=created_at_kst,
        Session_State="Active"
    )
    db.add(new_session)
    await db.commit()
    return new_session

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
    return session

# 세션 재개
async def resume_session(db: AsyncSession, session_id: int):
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 세션의 상태를 'Active'로 설정하고, 시작 시간을 업데이트
    session.Start_Edit = created_at_kst
    session.Session_State = "Active"
    await db.commit()

    # 마지막으로 편집한 결과와 관련된 데이터 조회
    if session.Last_Edit_result_id:
        last_edit_result = await db.get(Result, session.Last_Edit_result_id)
        if not last_edit_result:
            raise HTTPException(status_code=404, detail="Last edited result not found")

        # 해당 결과와 연관된 효과음 후보 조회
        effect_sounds = await db.execute(
            select(EffectSound).where(EffectSound.result_id == last_edit_result.result_id)
        )
        effect_sounds_data = effect_sounds.scalars().all()

        # 복원된 편집 상태 정보를 포함한 응답을 준비
        response_data = {
            "message": "Session Resumed",
            "last_edit_result": {
                "result_id": last_edit_result.result_id,
                "converted_result": last_edit_result.Converted_Result,
                "result_file_path": last_edit_result.ResultFilePath,
                "converted_date": last_edit_result.Converted_Date
            },
            "effect_sounds": [
                {
                    "effect_sound_id": effect_sound.effect_sound_id,
                    "effect_name": effect_sound.Effect_Name,
                    "effect_file_path": effect_sound.EffectFilePath
                } for effect_sound in effect_sounds_data
            ]
        }
        return response_data
    else:
        raise HTTPException(status_code=404, detail="No Last Edited Result to resume from")
    
