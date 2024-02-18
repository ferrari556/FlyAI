from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime

class EditHistory(Base):
    __tablename__ = 'edithistory'
    history_id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('result.result_id'))
    effect_sound_id = Column(Integer, ForeignKey('effectsound.effect_sound_id'), nullable=True) 
    Edit_Action = Column(String(30), nullable=False)
    EditDate = Column(DateTime, server_default=func.now())
    
    # Relationship
    result = relationship("Result", back_populates="edithistory")
    effectsound = relationship("EffectSounds")
    
class HistoryCreate(BaseModel):
    # session_id: int
    result_id: int
    Edit_Action: str
    # Original_Text: str
    # Edited_Text : str
    
class HistoryResponse(BaseModel):
    history_id : int
    result_id: int
    effect_sound_id : int
    EditDate : datetime
        
class EditText(BaseModel):
    result_id : int
    Edited_Text : str
    
class EditEffect(BaseModel):
    result_id : int 
    effect_sound_id : int
    
    