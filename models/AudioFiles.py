from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AudioFile(Base):
    __tablename__ = 'audioFiles'
    audio_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    audio_name = Column(String(50))
    FilePath = Column(String(100))
    File_Length = Column(Float)
    FileType = Column(String(30))
    Complete_Date = Column(DateTime)
    File_Status = Column(String(10))
    
    # 1:N 관계 설정
    user = relationship("User")