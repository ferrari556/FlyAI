from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EditSession(Base):
    __tablename__ = 'EditSession'
    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    audio_id = Column(Integer, ForeignKey('audioFiles.audio_id'))
    effect_id = Column(Integer, ForeignKey('Effectsounds.effect_id'))
    Edit_start = Column(DateTime)
    Edit_finish = Column(DateTime)
    Editposition = Column(Integer)
    session_status = Column(String(10))
    
    # 1:N 관계 설정
    user = relationship("User")
    audio_file = relationship("AudioFile")
    effect_sound = relationship("EffectSound")