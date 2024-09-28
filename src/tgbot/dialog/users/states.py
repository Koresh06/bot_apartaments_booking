from aiogram.fsm.state import State, StatesGroup


class StartSG(StatesGroup):
    search = State()



class LandlordStateSG(StatesGroup):
    register = State()
    name = State()
    phone = State()
    confirm = State()

class UserCatalogSG(StatesGroup):
    catalog = State()
    landlord = State()
