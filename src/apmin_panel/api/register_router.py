from fastapi import FastAPI

from .auth.router import router as auth_router
from .user.router import router as user_router
from .booking.router import router as bookings_router
from .landlord.router import router as landlords_router
from .statistic.router import router as statistics_router
from .booking.router import router as apartment_router


def register_routers(app: FastAPI) -> None:
    """Функция для регистрации всех роутеров в приложении."""
    
    app.include_router(auth_router)
    app.include_router(apartment_router)
    app.include_router(bookings_router)
    app.include_router(landlords_router)
    app.include_router(statistics_router)
    app.include_router(user_router)