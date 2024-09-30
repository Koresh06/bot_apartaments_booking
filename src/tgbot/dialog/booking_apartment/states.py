from aiogram.fsm.state import State, StatesGroup


class BookingApartmentSG(StatesGroup):
    start_date = State()
    end_date = State()
    confirm = State()


class ConfirmBooking(StatesGroup):
    start = State()
    cancle_message = State()
    cancle_сonfirm = State()
    

