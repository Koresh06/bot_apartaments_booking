from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    start = State()
    profile = State()
    faq = State()


class MenuLandlordSG(StatesGroup):
    start = State()
    register_apartament = State()
    current_apartments = State()


class RegisterApartmentSG(StatesGroup):
    city = State()
    street = State()
    house_number = State()
    apartment_number = State()
    price_per_day = State()
    rooms = State()
    description = State()
    photo = State()
    confirm = State()

class EditApartmentSG(StatesGroup):
    edit = State()
    city = State()
    street = State()
    house_number = State()
    apartment_number = State()
    price_per_day = State()
    rooms = State()
    description = State()
    photo = State()
    confirm_photos = State()


class LandlordApartmentsSG(StatesGroup):
    catalog = State()
    details = State()


