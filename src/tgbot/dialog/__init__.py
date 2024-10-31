from aiogram import Router
from aiogram_dialog import Dialog

from .apartments_landlord.landlord_apratments_dilalog import (
    menu_loandlord_dialog,
    register_apartament_dialog,
    my_apartmernt_landlord_dialog,
    edit_apartment_dialog,
    view_booking_orders_landlord,
    statistics_view_landlord,
)
from .apartments_landlord.register_landlord import register_landlord_dialog
from .apartments_users.apartments_filters_catalog import (
    filter_catalog_apartments_dialog,
    # city_filter_apartment_dialog,
    catalog_users_apartments_dialog,
    # price_range_filter_dialog,
    # rooms_filter_dialog,
)
from .booking_apartment.apartment_booking import booking_apartment, confirm_booking_landlord_dialog
from .admin.admin_dialog import register_name_city_dialog, main_admin_dialog, register_apartament_by_landlord_dialog


def get_all_dialogs() -> list[Dialog]:
    return [
        statistics_view_landlord,
        register_apartament_by_landlord_dialog,
        view_booking_orders_landlord,
        menu_loandlord_dialog,
        register_apartament_dialog,
        my_apartmernt_landlord_dialog,
        edit_apartment_dialog,
        register_landlord_dialog,
        filter_catalog_apartments_dialog,
        # city_filter_apartment_dialog,
        catalog_users_apartments_dialog,
        # price_range_filter_dialog,
        # rooms_filter_dialog,
        booking_apartment,
        confirm_booking_landlord_dialog,
        register_name_city_dialog,
        main_admin_dialog,
    ]


from .apartments_users.apartments_filters_catalog import router as catalog_router
from .admin.admin_dialog import router as admin_router
from .apartments_landlord.register_landlord import router as landLord_router
from .booking_apartment.apartment_booking import router as booking_apartment_router


def get_routers() -> list[Router]:
    return [
        booking_apartment_router,
        catalog_router,
        admin_router,
        landLord_router,
    ]




