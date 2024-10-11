from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles



templates = Jinja2Templates(directory="src/templates")


def configure_static(app):
    app.mount("/static", StaticFiles(directory="src/static"), name="static")