from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class STTData(Base):
    __tablename__ = 'STTdata'
    text_id = Column(Integer, primary_key=True)
    audio_id = Column(Integer, ForeignKey('audioFiles.audio_id'))
    Converted_text = Column(Text)
    Complete_Convert_Date = Column(DateTime)
    audio_file = relationship("AudioFile")