import os
from sanic import Sanic, json
from sanic.response import text
import redis.asyncio as redis

from app import create_app
from app.apis import api
from app.misc.log import log
from config import Config, LocalDBConfig

app = create_app(Config, LocalDBConfig)

app.ctx.redis = redis.from_url(Config.REDIS, decode_responses=True)

app.blueprint(api)

@app.route("/", methods={"GET", "POST"})
async def hello_world(request):
    return text("Hello World")

@app.route("/test-redis")
async def test_redis(request):
    try:
        pong = await request.app.ctx.redis.ping()
        return json({"redis": "connected", "pong": pong})
    except Exception as e:
        return json({"redis": "error", "detail": str(e)}, status=500)

if __name__ == '__main__':
    if 'SECRET_KEY' not in os.environ:
        log(message='SECRET KEY is not set in the environment variable.', keyword='WARN')
    app.run(**app.config['RUN_SETTING'])
