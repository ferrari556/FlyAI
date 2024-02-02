from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EditSession(Base):
    __tablename__ = 'EditSession'
    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))
    audio_id = Column(Integer, ForeignKey('AudioFile.audio_id'))
    result_id = Column(Integer, ForeignKey('Result.result_id'))
    Start_Edit = Column(DateTime)
    End_Edit = Column(DateTime)
    LastEditPoint = Column(Integer)
    Session_State = Column(String(50))
    
    # 1:N 관계 설정
    user = relationship("User")
    audio_file = relationship("AudioFile")
    result = relationship("Result")