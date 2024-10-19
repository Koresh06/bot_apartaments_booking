import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from src.apmin_panel.conf_static import configure_static
from src.core.config import config

from src.apmin_panel.api.auth.router import router as auth_router
from src.apmin_panel.api.booking.router import router as bookings_router
from src.apmin_panel.api.landlord.router import router as landlords_router
from src.apmin_panel.api.statistic.router import router as statistics_router
from src.apmin_panel.api.user.router import router as users_router
from src.apmin_panel.api.apartment.router import router as apartment_router


app = FastAPI()

configure_static(app)


@app.get("/")
async def root():
    return RedirectResponse(
        url="/auth/",
        status_code=status.HTTP_302_FOUND,
    )


app.include_router(auth_router)
app.include_router(apartment_router)
app.include_router(bookings_router)
app.include_router(landlords_router)
app.include_router(statistics_router)
app.include_router(users_router)


async def start_app():
    server_config = uvicorn.Config(
        "src.run_fastapi:app", 
        host=config.api.host,
        port=config.api.port,
        log_level="info",
        reload=True,
    )
    server = uvicorn.Server(server_config)
    await server.serve()