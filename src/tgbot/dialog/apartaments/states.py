from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    catalog = State()
    profile = State()
    faq = State()
