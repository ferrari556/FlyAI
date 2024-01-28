from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserSoundEffect(Base):
    __tablename__ = 'UserSoundEffects'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    effect_id = Column(Integer, ForeignKey('Effectsounds.effect_id'))
    
    # 1:N 관계 설정
    user = relationship("User")
    effect_sound = relationship("EffectSound")