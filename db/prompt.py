from sqlalchemy import Column, String, Text, Integer
from . import Base

class Prompt(Base):
    """Модель промпта."""
    __tablename__ = 'prompts'
    
    command = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    content = Column(Text)
    author = Column(Integer)
    admins = Column(String, default='[]')
    message_ids = Column(String, default='[]')
    groups = Column(String, default='[]')
