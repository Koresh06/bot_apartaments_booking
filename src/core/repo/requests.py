from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.apmin_panel.api.services.booking_api_service import BookingApiRepo
from src.apmin_panel.api.services.landlord_api_service import LandlordApiRepo
from src.apmin_panel.api.services.statistics_api_service import StatisticsApiRepo
from src.apmin_panel.api.services.users_api_service import UsersApiRepo
from src.tgbot.services.admin_service import AdminBotRepo
from src.tgbot.services.users_bot_service import BotUserRepo
from src.tgbot.services.apartments_bot_service import BotApartmentRepo
from src.tgbot.services.filter_apartment_service import FilterApartmentRepo
from src.tgbot.services.apartment_booking_service import ApartmentBookingRepo


@dataclass
class RequestsRepo:

    session: AsyncSession


    @property
    def bot_users(self) -> BotUserRepo:
        
        return BotUserRepo(self.session)
    

    @property
    def bot_apartments(self) -> BotApartmentRepo:
        
        return BotApartmentRepo(self.session)
    
    @property
    def filter_apartments(self) -> FilterApartmentRepo:
        
        return FilterApartmentRepo(self.session)
    
    @property
    def apartment_bookings(self) -> ApartmentBookingRepo:
        
        return ApartmentBookingRepo(self.session)
    

    @property
    def admin_bot(self) -> AdminBotRepo:
        
        return AdminBotRepo(self.session)
    

    @property
    def booking_api(self) -> BookingApiRepo:

        return BookingApiRepo(self.session)
    

    @property
    def landlord_api(self) -> LandlordApiRepo:

        return LandlordApiRepo(self.session)
    

    @property
    def statistics_api(self) -> StatisticsApiRepo:

        return StatisticsApiRepo(self.session)
    

    @property
    def users_api(self) -> UsersApiRepo:

        return UsersApiRepo(self.session)

