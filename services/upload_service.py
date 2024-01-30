from azure.storage.blob import BlobServiceClient
from models.AudioFiles import AudioFile
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

async def uploadtoazure(file_name: str, content_type: str, file_data, user_id: int, db: AsyncSession):
    connect_str = "DefaultEndpointsProtocol=https;AccountName=ferrari556;AccountKey=SY4SogqwL/eKbwJZz5BImza2nSWkiVpvkPKLVB1TVS9tR7HvUx4HHHFD0KzK7CsFLFV+XZ6EyDMP+AStEKIreg==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = "test"

    blob_client = blob_service_client.get_container_client(container_name).get_blob_client(file_name)
    blob_client.upload_blob(file_data)

    audio_file = AudioFile(
        user_id=user_id,
        audio_name=file_name,
        FilePath=f"{container_name}/{file_name}",
        File_Length=0,  # 예시로 0 설정, 실제 파일 길이 계산 필요
        FileType=content_type,
        Complete_Date=datetime.datetime.now(),
        File_Status="Uploaded"
    )

    db.add(audio_file)
    await db.commit()

    return audio_file

