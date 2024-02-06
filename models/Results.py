from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Result(Base):
    __tablename__ = 'Result'
    result_id = Column(Integer, primary_key=True)
    audio_id = Column(Integer, ForeignKey('AudioFile.audio_id'))
    Index = Column(Integer, nullable=False)
    Converted_Result = Column(String(255), nullable=False)
    Is_Text = Column(Boolean, nullable=False)
    EffectFilePath = Column(String(255), nullable=False)
    Converted_Date = Column(DateTime, nullable=False)
    
    # 1:N 관계 설정
    audio_file = relationship("AudioFile")