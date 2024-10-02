from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from src.apmin_panel.conf_static import configure_static


from src.apmin_panel.api.routers.auth import router as auth_router

app = FastAPI()

configure_static(app)


@app.get("/")
async def root():
    return RedirectResponse(
        url="/auth/login",
        status_code=status.HTTP_302_FOUND,
    )


app.include_router(auth_router)