from aiogram import Router
from aiogram_dialog import Dialog

from .apartments_landlord.landlord_apratments_dilalog import (
    menu_loandlord_dialog,
    register_apartament_dialog,
    my_apartmernt_landlord_dialog,
    edit_apartment_dialog,
)
from .apartments_landlord.register_landlord import register_landlord_dialog
from .apartments_users.apartments_filters_catalog import (
    filter_catalog_apartments_dialog,
    city_filter_apartment_dialog,
    catalog_users_apartments_dialog,
    price_range_filter_dialog,
    rooms_filter_dialog,
)
from .booking_apartment.apartment_booking import booking_apartment, confirm_booking_landlord_dialog
from .admin.admin_dialog import register_name_city_dialog, main_admin_dialog


def get_all_dialogs() -> list[Dialog]:
    return [
        menu_loandlord_dialog,
        register_apartament_dialog,
        my_apartmernt_landlord_dialog,
        edit_apartment_dialog,
        register_landlord_dialog,
        filter_catalog_apartments_dialog,
        city_filter_apartment_dialog,
        catalog_users_apartments_dialog,
        price_range_filter_dialog,
        rooms_filter_dialog,
        booking_apartment,
        confirm_booking_landlord_dialog,
        register_name_city_dialog,
        main_admin_dialog,
    ]


from .apartments_users.apartments_filters_catalog import router as catalog_router


def get_routers() -> list[Router]:
    return [
        catalog_router,
    ]




