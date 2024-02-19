from fastapi import APIRouter, Depends, UploadFile, File, WebSocket, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect
from datetime import datetime
import pytz, os, shutil, json
from config.database import get_db
from services.EffectSounds_service import (
    upload_effect_sound_to_azure,
    combine_audio_files_with_effects,
    combine_final_audio_files
)

router = APIRouter()

korea_time_zone = pytz.timezone("Asia/Seoul")
created_at_kst = datetime.now(korea_time_zone)

# 효과음 업로드
@router.post("/upload")
async def upload_effect_sound(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    
    # './tmp/' 디렉터리 존재 확인 및 생성
    tmp_directory = './tmp'
    if not os.path.exists(tmp_directory):
        os.makedirs(tmp_directory, exist_ok=True)

    # 파일 저장 경로 설정
    file_location = os.path.join(tmp_directory, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Azure Blob Storage에 업로드 및 데이터베이스에 저장
    effect_sound = await upload_effect_sound_to_azure(file.filename, file_location, db)
    
    # 모든 처리가 완료된 후 디렉토리 삭제
    if os.path.exists(tmp_directory):
        shutil.rmtree(tmp_directory)

    return {"filename": effect_sound.Effect_Name, "url": effect_sound.EffectFilePath}

# 효과음 + 오디오 분할 파일 합체
@router.post("/finalize/{audio_id}")
async def finalize_audio(audio_id: int, db: AsyncSession = Depends(get_db)):
    try:
        combined_audio_path = await combine_final_audio_files(db, audio_id)
        return {"message": "Audio combined successfully", "audio_path": combined_audio_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 유저에게 실시간으로 효과음 합성된 오디오 파일 들려주기
@router.websocket("/ws-interaction")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            # 클라이언트로부터 메시지를 기다립니다.
            data = await websocket.receive_text()
            # 데이터를 JSON으로 변환합니다.
            data_dict = json.loads(data)
            result_id = data_dict.get("result_id")
            effect_sound_id = data_dict.get("effect_sound_id")
            
            # 오디오 파일에 효과음 적용 로직을 구현
            combined_audio_path = await combine_audio_files_with_effects(db, result_id, effect_sound_id)
            
            # 클라이언트에게 결과 오디오 파일의 URL을 전송
            await websocket.send_text(combined_audio_path)
    except WebSocketDisconnect:
        print("Client disconnected")