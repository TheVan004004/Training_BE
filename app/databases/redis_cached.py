import json


async def set_cache(r, key, value, ttl=3000):
    await r.set(key, json.dumps(value), ex=ttl)


async def get_cache(r, key):
    value = await r.get(key)
    if value:
        value = json.loads(value)
    return value

async def delete_cache(r, key):
    await r.delete(key)