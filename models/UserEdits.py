from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserEdit(Base):
    __tablename__ = 'UserEdit'
    user_edit_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    audio_id = Column(Integer, ForeignKey('audioFile.audio_id'))
    effect_id = Column(Integer, ForeignKey('Effectsound.effect_id'))
    text_position = Column(Integer)
    effect_status = Column(String(50))
    session_status = Column(String(50))
    
    # 1:N 관계 설정
    user = relationship("User")
    audio_file = relationship("AudioFile")
    effect_sound = relationship("EffectSound")