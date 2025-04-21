from sqlalchemy import Column, Integer, String
from . import Base

class Context(Base):
    """Модель контекста."""
    __tablename__ = 'contexts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    chat_id = Column(Integer)
    prompt_command = Column(String)
    context_data = Column(String)