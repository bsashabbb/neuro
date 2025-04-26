from aiogram.filters.callback_data import CallbackData

class TrueDelAllContext(CallbackData, prefix='true_del_all_context'):
    initiator: int

class FalseDelAllContext(CallbackData, prefix='false_del_all_context'):
    initiator: int

class DelContext(CallbackData, prefix='del_context'):
    command: str

class TrueDelContext(CallbackData, prefix='true_del_context'):
    command: str
    initiator: int

class FalseDelContext(CallbackData, prefix='false_del_context'):
    initiator: int

class TrueDelPrompt(CallbackData, prefix='true_delprompt'):
    command: str
    initiator: int

class FalseDelPrompt(CallbackData, prefix='false_delprompt'):
    initiator: int

class Del(CallbackData, prefix='del'):
    initiator:int

class SettingPicturesInChat(CallbackData, prefix='pictures_in_chat'):
    status: str

class SettingPicturesCount(CallbackData, prefix='pictures_count'):
    count: int

class SettingImageAI(CallbackData, prefix='imageai'):
    ai: str
