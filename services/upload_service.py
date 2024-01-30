from azure.storage.blob import BlobServiceClient
from models.AudioFiles import AudioFile
from sqlalchemy.ext.asyncio import AsyncSession
import pytz, datetime
from sqlalchemy.future import select

# 사용자 ID로 사용자 검색
async def get_user_by_file_name(db: AsyncSession, file_name: str):
    result = await db.execute(select(AudioFile).filter_by(audio_name=file_name))
    return result.scalar_one_or_none()

async def uploadtoazure(file_name: str, content_type: str, file_data, user_id: int, db: AsyncSession):

    # 사용자 존재 여부 확인
    existing_user = await get_user_by_file_name(db, file_name)
    
    if not existing_user:
        raise ValueError("User Not Found")
    
    connect_str = "DefaultEndpointsProtocol=https;AccountName=ferrari556;AccountKey=SY4SogqwL/eKbwJZz5BImza2nSWkiVpvkPKLVB1TVS9tR7HvUx4HHHFD0KzK7CsFLFV+XZ6EyDMP+AStEKIreg==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = "test"

    blob_client = blob_service_client.get_container_client(container_name).get_blob_client(file_name)
    blob_client.upload_blob(file_data)

    # 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
    korea_time_zone = pytz.timezone("Asia/Seoul")
    created_at_kst = datetime.now(korea_time_zone)
        
    audio_file = AudioFile(
        user_id=user_id,
        audio_name=file_name,
        FilePath=f"{container_name}/{file_name}",
        File_Length=0,  # 예시로 0 설정, 실제 파일 길이 계산 필요
        FileType=content_type,
        Complete_Date=created_at_kst,
        File_Status="Uploaded"
    )

    db.add(audio_file)
    await db.commit()

    return audio_file

