from typing import List, Optional
from sqlalchemy import delete, select

from src.core.repo.base import BaseRepo
from src.core.models import Users, Landlords, ApartmentPhoto, Apartment, City, Booking


class BotApartmentRepo(BaseRepo):

    async def check_landlord(self, tg_id: int) -> bool:
        result = await self.session.scalar(
            select(Landlords).join(Users).where(Users.tg_id == tg_id)
        )

        return result is not None

    async def register_apartment_landlord(self, tg_id: int, data: dict) -> bool:
        stmt: Landlords = await self.session.scalar(
            select(Landlords).join(Users).where(Users.tg_id == tg_id)
        )

        params = Apartment(
            landlord_id=stmt.id,
            city_id=int(data["city_id"]),
            street=data["street"],
            house_number=data["house_number"],
            apartment_number=data["apartment_number"],
            price_per_day=data["price_per_day"],
            rooms=data["rooms"],
            description=data["description"],
        )
        self.session.add(params)
        await self.session.commit()
        await self.session.refresh(params)

        photos = ApartmentPhoto(
            apartment_id=params.id,
            photos_ids=data["photos"],
        )
        self.session.add(photos)
        await self.session.commit()
        await self.session.refresh(photos)

        return True

    async def get_catalog_apartments_landlord(self, tg_id: int) -> Optional[List[dict]]:
        landlord_stmt = await self.session.scalar(
            select(Landlords).join(Users).where(Users.tg_id == tg_id)
        )

        if not landlord_stmt:
            return None  


        stmt = (
            select(Apartment, ApartmentPhoto, City.name)
            .where(Apartment.landlord_id == landlord_stmt.id)
            .outerjoin(ApartmentPhoto, ApartmentPhoto.apartment_id == Apartment.id)
            .join(City, City.id == Apartment.city_id)
            .order_by(Apartment.id.desc())
        )

        result = await self.session.execute(stmt)
        apartments = result.all()

        if not apartments or not any(apartment for apartment, *_ in apartments):
            return False
        
        formatted_result = []
        for apartment, photo, city_name in apartments:
            formatted_result.append(
                {
                    "apartment_id": apartment.id,
                    "landlord_id": apartment.landlord_id,
                    "landlord_tg_id": tg_id,  
                    "city": city_name,
                    "street": apartment.street,
                    "house_number": apartment.house_number,
                    "apartment_number": apartment.apartment_number if apartment.apartment_number else "-",
                    "price_per_day": apartment.price_per_day,
                    "rooms": apartment.rooms,
                    "description": apartment.description,
                    "is_available": (
                        "✅ Свободно" if apartment.is_available else "❌ Занято"
                    ),
                    "photos": photo.photos_ids if photo else [], 
                }
            )

        return formatted_result
    

    async def landlord_info(self, id: int):
        stmt = (
            select(Landlords, Users)
            .join(Users, Landlords.user_id == Users.id)
            .where(Landlords.id == id)
        )
        result = await self.session.execute(stmt)
        landlord, user = result.first()
        return {
            "landlord": landlord,
            "user": user
        }
    


    async def check_apartment_landlord(
        self,
        tg_id: int,
        apartment_id: int,
    ) -> bool:
    
        apartment_info: Apartment = await self.session.scalar(
            select(Apartment).where(Apartment.id == apartment_id)
        )

        if not apartment_info:
            return None 

        landlord_info = await self.session.scalar(
            select(Landlords)
            .where(Landlords.id == apartment_info.landlord_id)
            .join(Users)
            .where(Users.tg_id == tg_id)
        )

        if not landlord_info:
            return None 

        return apartment_info

    async def update_apartment_info(
        self,
        tg_id: int,
        apartment_id: int,
        widget_id: int,
        text: str | int,
    ) -> bool:

        apartment_info: Apartment = await self.check_apartment_landlord(
            tg_id=tg_id, apartment_id=apartment_id
        )
        if not apartment_info:
            return False 

        # Обновляем информацию
        if widget_id == "city":
            apartment_info.city_id = text
        elif widget_id == "street":
            apartment_info.street = text
        elif widget_id == "house_number":
            apartment_info.house_number = text
        elif widget_id == "apartment_number":
            apartment_info.apartment_number = text
        elif widget_id == "price_per_day":
            apartment_info.price_per_day = text
        elif widget_id == "rooms":
            apartment_info.rooms = text
        elif widget_id == "description":
            apartment_info.description = text

        await self.session.commit()
        return True  

    async def update_apartment_photos(
        self,
        tg_id: int,
        apartment_id: int,
        photos_ids: List[str],
    ) -> bool:
        apartment_info: Apartment = await self.check_apartment_landlord(
            tg_id=tg_id,
            apartment_id=apartment_id,
        )
        if not apartment_info:
            return False 

        await self.session.execute(
            delete(ApartmentPhoto).where(ApartmentPhoto.apartment_id == apartment_id)
        )

        new_photo = ApartmentPhoto(apartment_id=apartment_id, photos_ids=photos_ids)
        self.session.add(new_photo)

        await self.session.commit()
        return True 

    async def delete_apartment_landlord(
        self,
        tg_id: int,
        apartment_id: int,
    ) -> bool:
        apartment_info: Apartment = await self.check_apartment_landlord(
            tg_id=tg_id,
            apartment_id=apartment_id,
        )
        if not apartment_info:
            return False

        await self.session.execute(
            delete(ApartmentPhoto).where(ApartmentPhoto.apartment_id == apartment_id)
        )

        await self.session.execute(
            delete(Booking).where(Booking.apartment_id == apartment_id)
        )

        await self.session.execute(
            delete(Apartment).where(Apartment.id == apartment_id)
        )

        await self.session.commit()
        return True

    async def update_is_available(
            self,
            tg_id: int,
            apartment_id: int,
        ) -> Optional[bool]: 
        apartment_info: Apartment = await self.check_apartment_landlord(
            tg_id=tg_id,
            apartment_id=apartment_id,
        )
    
        if apartment_info is None:
            return None  
    
        apartment_info.is_available = not apartment_info.is_available 
    
        await self.session.commit()
    
        return apartment_info.is_available 
    

    async def get_orders_bookings(self, tg_id: int) -> Optional[List[dict]]:
        landlord_stmt = await self.session.scalar(
            select(Landlords).join(Users).where(Users.tg_id == tg_id)
        )

        if not landlord_stmt:
            return None

        stmt = (
            select(Booking, Apartment, City.name)
            .join(Apartment, Booking.apartment_id == Apartment.id)
            .join(City, Apartment.city_id == City.id)
            .where(Apartment.landlord_id == landlord_stmt.id)
            .where(Booking.is_confirmed == False) 
            .order_by(Booking.create_at.desc())   
        )

        result = await self.session.execute(stmt)

        apartments_info = []
        for booking, apartment, city_name in result.all():
            apartments_info.append({
                "booking": booking,
                "apartment_id": apartment.id,
                "landlord_id": apartment.landlord_id,
                "landlord_tg_id": tg_id,
                "city": city_name,
                "street": apartment.street,
                "house_number": apartment.house_number,
                "apartment_number": apartment.apartment_number if apartment.apartment_number else "-",
                "price_per_day": apartment.price_per_day,
                "rooms": apartment.rooms,
                "description": apartment.description,
                "booking_start_date": booking.start_date.strftime("%d.%m.%Y"),
                "booking_end_date": booking.end_date.strftime("%d.%m.%Y"),
            })

        return apartments_info if apartments_info else False


    async def get_statistics_view(self, tg_id: int) -> Optional[str]:
        stmt = (
            select(Landlords)
            .join(Users)
            .where(Users.tg_id == tg_id)
        )
        landlord: Landlords = await self.session.scalar(stmt)

        if not landlord:
            return None

        # Обработка данных и замена месяцев на русские названия
        month_names = {
            "01": "Январь", "02": "Февраль", "03": "Март", "04": "Апрель",
            "05": "Май", "06": "Июнь", "07": "Июль", "08": "Август",
            "09": "Сентябрь", "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"
        }

        filtered_stats = {}
        for date_str, count in landlord.count_clicks_phone.items():
            year, month = date_str.split('-')[1], date_str.split('-')[0]
            if year not in filtered_stats:
                filtered_stats[year] = {}
            filtered_stats[year][month_names[month]] = count

        # message_text = "📊 Статистика просмотров по месяцам:\n"
        # for year, months in filtered_stats.items():
        #     message_text += f"\n📅 {year} год:\n"
        #     for month, count in months.items():
        #         message_text += f"  **{month}**: {count}\n"

        if filtered_stats == {}:
            return None

        return filtered_stats
    

    async def get_statistics_view_apartment(self, apartment_id: int) -> Optional[str]:
        stmt = (
            select(Apartment)
            .where(Apartment.id == apartment_id)
        )
        apartment: Apartment = await self.session.scalar(stmt)

        if not apartment:
            return None

        # Обработка данных и замена месяцев на русские названия
        month_names = {
            "01": "Январь", "02": "Февраль", "03": "Март", "04": "Апрель",
            "05": "Май", "06": "Июнь", "07": "Июль", "08": "Август",
            "09": "Сентябрь", "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"
        }

        filtered_stats = {}
        for date_str, count in apartment.count_contact_views.items():
            year, month = date_str.split('-')[1], date_str.split('-')[0]
            if year not in filtered_stats:
                filtered_stats[year] = {}
            filtered_stats[year][month_names[month]] = count

        if filtered_stats == {}:
            return None

        return filtered_stats