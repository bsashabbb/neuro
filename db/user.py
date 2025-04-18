from sqlalchemy import Column, Integer, String, Boolean
from . import Base
import json
from aiogram import types

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    banned = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    object = Column(String)

    def get_object(self) -> types.User:
        data = json.loads(self.object)
        return types.User(**data)
    
    def set_object(self, user: types.User):
        self.object = user.model_dump_json()
