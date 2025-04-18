from sqlalchemy import Column, Integer, String, Boolean
from . import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    banned = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
