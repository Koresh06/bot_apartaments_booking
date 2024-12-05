import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from src.core.config import config
from src.apmin_panel.api.register_router import register_routers
from src.apmin_panel.conf_static import configure_static



app = FastAPI()

configure_static(app)


@app.get("/")
async def root():
    return RedirectResponse(
        url="/auth/",
        status_code=status.HTTP_302_FOUND,
    )


register_routers(app)

async def start_app():
    server_config = uvicorn.Config(
        "src.run_fastapi:app", 
        host=config.api.host,
        port=config.api.port,
        log_level="info",
    )
    server = uvicorn.Server(server_config)
    await server.serve()