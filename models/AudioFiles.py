from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime

class AudioFile(Base):
    __tablename__ = 'AudioFile'
    audio_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))
    File_Name = Column(String(255))
    FilePath = Column(String(255))
    File_Length = Column(Float)
    FileType = Column(String(50))
    Upload_Date = Column(DateTime)
    File_Status = Column(String(50))
    
    # 1:N 관계 설정
    user = relationship("User")

class AudioResponse(BaseModel):
    audio_id : int
    File_Name : str
    FileType : str
    Upload_Date : datetime
    File_Status : str
    
class AudioDelete(BaseModel):
    File_Name : str
    FileType : str
    Upload_Date : datetime

class AudioRead(BaseModel):
    File_Name : str
    FileType : str
    Upload_Date : datetime
    File_Status : str