from db import get_db
from db.prompt import Prompt

def add_or_update_prompt(command, name, description, content, author):
    with get_db() as db:
        prompt = db.query(Prompt).filter_by(command=command).first()
        if prompt:
            prompt.name = name
            prompt.description = description
            prompt.content = content
            yield True
        else:
            prompt = Prompt(command=command, name=name, description=description, content=content, author=author)
            db.add(prompt)
            yield False
        db.commit()

def del_prompt(command):
    with get_db() as db:
        prompt = db.query(Prompt).filter_by(command=command).first()
        db.delete(prompt)
        db.commit()
