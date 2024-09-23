from aiogram.fsm.state import State, StatesGroup


class StartSG(StatesGroup):
    new_search = State()
    current_start = State()



class LandlordStateSG(StatesGroup):
    register = State()
    name = State()
    phone = State()
    confirm = State()

class UserCatalogSG(StatesGroup):
    catalog = State()