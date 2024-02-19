from fastapi import APIRouter, Depends, UploadFile, File, WebSocket, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect
from datetime import datetime
import pytz, os, shutil, json
from config.database import get_db
from services.EffectSounds_service import (
    upload_effect_sound_to_azure,
    combine_audio_files_with_effects,
    combine_final_audio_files,
    combine_whole_audio_with_effects
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

@router.websocket("/ws-play")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)

            result_id = data_dict.get("result_id")
            effect_sound_id = data_dict.get("effect_sound_id", None)  # 효과음 적용 여부

            # 오디오 데이터 바이트를 받아오는 로직
            audio_data_bytes = await combine_audio_files_with_effects(db, result_id, effect_sound_id)
            
            if audio_data_bytes:
                await websocket.send_bytes(audio_data_bytes)
            else:
                await websocket.send_text("Error: Unable to process audio")
    except WebSocketDisconnect:
        print("Client disconnected")
        
@router.websocket("/ws-whole-play")
async def websocket_whole_audio_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)

            audio_id = data_dict.get("audio_id")
            audio_data_bytes = await combine_whole_audio_with_effects(db, audio_id)
            
            if audio_data_bytes:
                await websocket.send_bytes(audio_data_bytes)
            else:
                await websocket.send_text("Error: Unable to process audio")
    except WebSocketDisconnect:
        print("Client disconnected")