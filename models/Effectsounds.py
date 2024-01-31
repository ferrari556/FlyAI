from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EffectSound(Base):
    __tablename__ = 'Effectsound'
    effect_id = Column(Integer, primary_key=True)
    effect_name = Column(String(255))
    effect_path = Column(String(255))
    effect_length = Column(Float)
    effect_index = Column(Integer)