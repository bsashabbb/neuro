from db import get_db
from db.prompt import Prompt

def add_or_update_prompt(command, name, description, content, author=None):
    with get_db() as db:
        prompt = db.query(Prompt).filter_by(command=command).first()
        if prompt:
            prompt.name = name
            prompt.description = description
            prompt.content = content
            status = True
        else:
            prompt = Prompt(command=command, name=name, description=description, content=content, author=author)
            db.add(prompt)
            status = False
        db.commit()
        db.refresh(prompt)
    return status

def del_prompt(command):
    with get_db() as db:
        prompt = db.query(Prompt).filter_by(command=command).first()
        db.delete(prompt)
        db.commit()
