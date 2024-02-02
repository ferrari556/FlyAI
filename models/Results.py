from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Result(Base):
    __tablename__ = 'Result'
    result_id = Column(Integer, primary_key=True)
    audio_id = Column(Integer, ForeignKey('AudioFile.user_id'))
    Text_Index = Column(Integer)
    OriginalText = Column(String(255))
    EffectStatus = Column(Boolean)
    EffectFilePath = Column(String(255))
    EffectDescription = Column(String(50))
    Converted_Date = Column(DateTime)
    
    # 1:N 관계 설정
    audio_file = relationship("AudioFile")