from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from . import Base
import json
from aiogram import types

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    banned = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    object = Column(String)
    settings = Column(String, default='{"reset": true, "pictures_in_dialog": true, "pictures_count": 5, "imageai": "sd"}')
    created_at = Column(DateTime, default=func.now())

    def get_object(self) -> types.User:
        data = json.loads(self.object)
        return types.User(**data)
    
    def set_object(self, user: types.User):
        self.object = user.model_dump_json()
