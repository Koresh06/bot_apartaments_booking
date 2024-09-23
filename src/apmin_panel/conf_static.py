from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles



# Настраиваем пути к шаблонам
templates = Jinja2Templates(directory="src/templates")


# Функция для настройки статики
def configure_static(app):
    app.mount("/static", StaticFiles(directory="src/static"), name="static")