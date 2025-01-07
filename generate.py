import requests


def onlinegen(prompt):
    response = requests.post('https://api.r00t.us.kg/v1/chat/simple/gpt', json={"prompt": prompt})
    return response.text


def geminigen():
    pass


def sluxgen():
    pass


def sdgen():
    pass


def kandgen():
    pass
