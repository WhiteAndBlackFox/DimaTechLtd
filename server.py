from sanic import Sanic
from sanic.response import text

from database import close_db, init_db

app = Sanic("dima_tech_ltd")


@app.before_server_start
async def setup_db(app, loop):
    await init_db()


@app.after_server_stop
async def teardown_db(app, loop):
    await close_db()


@app.get("/")
async def hello_world(request):
    return text("Hello, world.")