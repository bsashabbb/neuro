from sqlalchemy import Column, Integer, String, Text
from . import Base

class PromptGroup(Base):
    """Модель групп промптов."""
    __tablename__ = 'prompt_groups'
    
    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String)
    description = Column(Text)
    creator_id = Column(Integer)
