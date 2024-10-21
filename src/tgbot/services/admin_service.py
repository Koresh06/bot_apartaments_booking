from src.core.repo.base import BaseRepo
from src.core.models import City, Users, Landlords, Apartment, ApartmentPhoto
from sqlalchemy import select


class AdminBotRepo(BaseRepo):
    
    async def register_name_city(self, name: str) -> City:
        city = City(name=name)
        self.session.add(city)
        await self.session.commit()
        await self.session.refresh(city)
        return city
    

    async def check_is_admin(self, tg_id: int) -> bool:
        stmt = select(Users).where(Users.tg_id == tg_id)
        result = await self.session.scalar(stmt)
        return result
    
    async def get_landlords(self) -> list:
        stmt = select(Landlords.id, Landlords.company_name).order_by(Landlords.id)
        result = await self.session.execute(stmt)
        landlords = result.all()

        return [(landlord_id, name) for landlord_id, name in landlords]        
    

    async def admin_register_apartment_landlord(self, landlord_id: int, data: dict) -> bool:
        stmt = select(Landlords).where(Landlords.id == landlord_id)

        params = Apartment(
            landlord_id=landlord_id,
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