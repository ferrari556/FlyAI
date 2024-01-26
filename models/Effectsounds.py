from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EffectSound(Base):
    __tablename__ = 'Effectsounds'
    effect_id = Column(Integer, primary_key=True)
    effect_name = Column(String(50))
    Effect_Path = Column(String(100))
    Effect_Length = Column(Float)
    Effect_number = Column(Integer)