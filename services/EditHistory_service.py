from models.EditHistory import EditHistory, EditText, EditEffect
from models.EditSession import EditSession
from models.Results import Result
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import pytz
from datetime import datetime

# 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
korea_time_zone = pytz.timezone("Asia/Seoul")
created_at_kst = datetime.now(korea_time_zone)

# 편집 기록 확인
async def get_edithistory_by_id(db: AsyncSession, history_id: int):
    history = await db.get(EditHistory, history_id)
    if history is None:
        raise HTTPException(status_code=404, detail="EditHistory not found")
    return history

# 편집 기록 생성 및 세션 업데이트
async def create_edit_history_and_update_session(
        db: AsyncSession, session_id: int, result_id: int, edit_action: str = "", 
        original_text: str = "",edited_text: str = "", effect_sound_id: int = None):
    
    # 편집 이력 생성
    new_history = EditHistory(
        session_id=session_id,
        result_id=result_id,
        Edit_Action=edit_action,
        Original_Text=original_text,
        Edited_Text=edited_text,
        Effect_Sound_ID=effect_sound_id,
        EditDate=created_at_kst
    )
    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)

    # 세션 업데이트
    edit_session = await db.get(EditSession, session_id)
    if edit_session:
        edit_session.Last_Edit_result_id = new_history.result_id  # 마지막 편집 결과 ID 업데이트
        await db.commit()
    else:
        raise HTTPException(status_code=404, detail="EditSession not found")

    return new_history

# 편집 기록 삭제
async def delete_edithistory(db: AsyncSession, history_id: int):
    existing_history = await db.get(EditHistory, history_id)
    if existing_history is None:
        raise HTTPException(status_code=404, detail="EditHistory not found")

    await db.delete(existing_history)
    await db.commit()
    
# 사용자가 텍스트를 변경했을 때 발생하는 함수
async def edit_text(db: AsyncSession, request: EditText):
    result = await db.get(Result, request.result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    new_history = EditHistory(
        session_id=request.session_id,
        result_id=request.result_id,
        Edit_Action="Convert Text",
        Original_Text=result.Converted_Result,
        Edited_Text=request.Edited_Text,
        EditDate=created_at_kst
    )

    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)

     # EditSession 업데이트
    edit_session = await db.get(EditSession, request.session_id)
    if edit_session:
        edit_session.Last_Edit_result_id = request.result_id
        await db.commit()

    return new_history

# 효과음을 채택했을 때 실행되는 함수
async def apply_effect(db: AsyncSession, request : EditEffect):
    result = await db.get(Result, request.result_id)

    new_history = EditHistory(
        session_id=request.session_id,
        result_id=result.result_id,
        Original_Text=result.Converted_Result,
        Edited_Text=result.Converted_Result,
        Edit_Action="Apply Effect",
        EditDate=created_at_kst
    )

    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)

    # EditSession 업데이트
    edit_session = await db.get(EditSession, request.session_id)
    if edit_session:
        edit_session.Last_Edit_result_id = request.result_id
        await db.commit()

    return new_history

# 이펙트 선택을 안하면 실행되는 함수
async def cancel_effect(db: AsyncSession, request : EditEffect):
    created_at_kst = datetime.now(korea_time_zone)
    result = await db.get(Result, request.result_id)

    new_history = EditHistory(
        session_id=request.session_id,
        result_id=result.result_id,
        Original_Text=result.Converted_Result,
        Edited_Text=result.Converted_Result,
        Edit_Action="Cancel Effect",
        EditDate=created_at_kst
    )

    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)

    # EditSession 업데이트
    edit_session = await db.get(EditSession, request.session_id)
    if edit_session:
        edit_session.Last_Edit_result_id = request.result_id
        await db.commit()

    return new_history

