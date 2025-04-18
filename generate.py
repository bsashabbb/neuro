import httpx
from utils.http_client import get_client
import base64
from typing import Optional, List, Dict, Tuple

OPO_API = 'https://api.opo.pp.ru/'


async def onlinegen(prompt):
    async with get_client() as client:
        response = await client.post(f'{OPO_API}v1/chat/simple/gpt', json={"prompt": prompt})
    return response.text

async def fluxgen(prompt):
    async with get_client() as client:
        response = await client.post(f'{OPO_API}v1/image/flux', json={"prompt": prompt})
    return response.text


async def sdgen(prompt):
    async with get_client() as client:
        response = await client.post(f'{OPO_API}v1/image/sd', json={"prompt": prompt})
    return response.text


def kandgen():
    pass
