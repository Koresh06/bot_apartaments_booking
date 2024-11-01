from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    start = State()
    profile = State()
    faq = State()


class LandlordStateSG(StatesGroup):
    register = State()
    name = State()
    phone = State()
    confirm = State()


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
    view = State()


class OrdersBookingSG(StatesGroup):
    orders = State()
    cancel_message = State()
    cancle_сonfirm = State()


class StatisticsViewSG(StatesGroup):
    start = State()


class BookingInformationSG(StatesGroup):
    start = State()

