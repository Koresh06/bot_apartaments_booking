from aiogram.fsm.state import State, StatesGroup


class MainAdminSG(StatesGroup):
    start = State()

class RegisterNameCitysSG(StatesGroup):
    start = State()
    confirm = State()