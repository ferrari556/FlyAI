from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime

class AudioFile(Base):
    __tablename__ = 'audioFile'
    audio_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    audio_name = Column(String(50))
    FilePath = Column(String(100))
    File_Length = Column(Float)
    FileType = Column(String(30))
    Complete_Date = Column(DateTime)
    File_Status = Column(String(10))
    
    # 1:N 관계 설정
    user = relationship("User")

class AudioResponse(BaseModel):
    audio_id : int
    audio_name : str
    FileType : str
    Complete_Data : datetime
    File_Status : str
    
class AudioDownload(BaseModel):
    audio_name : str
    Filepath : str