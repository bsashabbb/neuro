from sqlalchemy import Column, Integer, String
from . import Base

class APIKey(Base):
    """Модель API ключей."""
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, index=True)  # Unique key ID
    key = Column(String)  # API key
    creator = Column(Integer)
