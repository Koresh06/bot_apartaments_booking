import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from src.core.config import config
from src.apmin_panel.api.register_router import register_routers
from src.apmin_panel.conf_static import configure_static
from src.setup_logging import setup_main_logging


def create_app():
    app = FastAPI()

    configure_static(app)
    register_routers(app)


    @app.get("/")
    async def root():
        return RedirectResponse(
            url="/auth/",
            status_code=status.HTTP_302_FOUND,
        )
    
    return app
    
if __name__ == "__main__":
    try:
        setup_main_logging()
        uvicorn.run(
            app=create_app(),
            host=config.api.host,
            port=config.api.port,
            log_level="info",
        )
    except KeyboardInterrupt as e:
        print("Программа завершена пользователем")
