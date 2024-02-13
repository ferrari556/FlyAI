from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime

class EditHistory(Base):
    __tablename__ = 'edithistory'
    history_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('editsession.session_id'))
    result_id = Column(Integer, ForeignKey('result.result_id'))
    effect_sound_id = Column(Integer, ForeignKey('effectsound.effect_sound_id'), nullable=True) 
    Edit_Action = Column(String(30), nullable=False)
    Original_Text = Column(String(255), nullable=True)
    Edited_Text = Column(String(255), nullable=True)
    EditDate = Column(DateTime, server_default=func.now())
    
    # Relationship
    session = relationship("EditSession", back_populates="edithistory")
    result = relationship("Result", back_populates="edithistory")
    effectsound = relationship("EffectSound")
    
class HistoryCreate(BaseModel):
    session_id: int
    result_id: int
    Edit_Action: str
    Original_Text: str
    Edited_Text : str
    
class HistoryResponse(BaseModel):
    history_id : int
    session_id: int
    result_id: int
    effect_sound_id : int
    EditDate : datetime
        
class EditText(BaseModel):
    session_id : int
    result_id : int
    Edited_Text : str
    
class EditEffect(BaseModel):
    session_id : int
    result_id : int 
    
    