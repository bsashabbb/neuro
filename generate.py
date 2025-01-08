import requests


def onlinegen(prompt):
    response = requests.post('https://api.r00t.us.kg/v1/chat/simple/gpt', json={"prompt": prompt})
    return response.text


def geminigen():
    pass


def fluxgen(prompt):
    response = requests.post('https://api.r00t.us.kg/v1/image/flux', json={"prompt": prompt})
    return response.text


def sdgen(prompt):
    response = requests.post('https://api.r00t.us.kg/v1/image/sd', json={"prompt": prompt})
    return response.text


def kandgen():
    pass
