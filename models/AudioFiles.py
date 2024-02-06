from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime

class AudioFile(Base):
    __tablename__ = 'AudioFile'
    audio_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))
    File_Name = Column(String(255), nullable=False)
    FilePath = Column(String(255), nullable=False)
    File_Length = Column(Float, nullable=False)
    FileType = Column(String(50), nullable=False)
    Upload_Date = Column(DateTime, nullable=False)
    File_Status = Column(String(50), nullable=False)
    
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