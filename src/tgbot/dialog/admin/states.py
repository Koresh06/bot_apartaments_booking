from aiogram.fsm.state import State, StatesGroup


class MainAdminSG(StatesGroup):
    start = State()


class RegisterNameCitysSG(StatesGroup):
    start = State()
    confirm = State()


class RegisterApartmentLandlordSG(StatesGroup):
    landlord = State()
    city = State()
    street = State()
    house_number = State()
    apartment_number = State()
    price_per_day = State()
    rooms = State()
    description = State()
    photo = State()
    confirm = State()
