from contextlib import asynccontextmanager
import httpx

_client = None

@asynccontextmanager
async def get_client(proxy=None):
    global _client
    
    if _client is None:
        _client = httpx.AsyncClient(
            proxy=proxy,
            timeout=150.0
        )
        await _client.__aenter__()
    
    try:
        yield _client
    finally:
        if _client:
            await _client.__aexit__(None, None, None)
            _client = None
