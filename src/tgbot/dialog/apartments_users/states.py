from aiogram.fsm.state import State, StatesGroup


class FiltersApartmentsSG(StatesGroup):
    start = State()

    
class FilterCitysSG(StatesGroup):
    start = State()


class FilterPricePerDaySG(StatesGroup):
    min_price = State()
    max_price = State()
    confirm = State()



class FilterRoomsSG(StatesGroup):
    start = State()


class FilteredCatalogApartmentsSG(StatesGroup):
    start = State()
    details = State()

