from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from src.apmin_panel.conf_static import configure_static


from src.apmin_panel.api.routers.auth import router as auth_router
from src.apmin_panel.api.routers.bookings import router as bookings_router
from src.apmin_panel.api.routers.landlords import router as landlords_router

app = FastAPI()

configure_static(app)


@app.get("/")
async def root():
    return RedirectResponse(
        url="/auth/login",
        status_code=status.HTTP_302_FOUND,
    )


app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(landlords_router)