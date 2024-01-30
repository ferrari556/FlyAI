from azure.storage.blob import BlobServiceClient
from models.AudioFiles import AudioFile
from sqlalchemy.ext.asyncio import AsyncSession
import pytz, datetime
from sqlalchemy.future import select
from mutagen.mp3 import MP3
import os

# 파일 이름으로 오디오 파일 검색
async def get_audiofile_by_name(db: AsyncSession, file_name: str):
    result = await db.execute(select(AudioFile).filter_by(audio_name=file_name))
    return result.scalar_one_or_none()

async def uploadtoazure(file_name: str, content_type: str, file_data, user_id: int, db: AsyncSession):
    # 파일 이름으로 기존 오디오 파일 존재 여부 확인
    existing_audiofile = await get_audiofile_by_name(db, file_name)
    
    if existing_audiofile:
        raise ValueError("File Name Already Used")

    # 로컬 경로에 파일 임시 저장
    temp_file_path = f"./tmp/{file_name}"
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_data)

    try:
        # MP3 파일의 재생 시간 계산
        audio = MP3(temp_file_path)
        file_length = audio.info.length  # 재생 시간 (초 단위)

        # Azure에 파일 업로드
        connect_str = "DefaultEndpointsProtocol=https;AccountName=ferrari556;AccountKey=g8BUEJyJPPinwIYo7QPyAZql3SHflcOXQHFfBSqWijNdor0uC3+2MFslBA16+AnoVvrT1G93xUQe+AStXt7N4g==;EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = "test"
        blob_client = blob_service_client.get_container_client(container_name).get_blob_client(file_name)
        blob_client.upload_blob(file_data)

        # 데이터베이스 업데이트
        korea_time_zone = pytz.timezone("Asia/Seoul")
        created_at_kst = datetime.datetime.now(korea_time_zone)

        audio_file = AudioFile(
            user_id=user_id,
            audio_name=file_name,
            FilePath=f"{container_name}/{file_name}",
            File_Length=file_length,  # 실제 파일 길이로 설정
            FileType=content_type,
            Complete_Date=created_at_kst,
            File_Status="Uploaded"
        )

        db.add(audio_file)
        await db.commit()
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return audio_file