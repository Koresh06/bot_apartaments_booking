from typing import Optional, Union
from pydantic import BaseModel
from datetime import date
from fastapi import Form


class LandlordDateSchema(BaseModel):
    landlord_id: int
    start_date: Optional[Union[date, None]] = None 
    end_date: Optional[Union[date, None]] = None   

    @classmethod
    def as_form(
        cls,
        landlord_id: int = Form(...),
        start_date: Optional[str] = Form(None), 
        end_date: Optional[str] = Form(None),  
    ):
        def parse_date(date_str: Optional[str]) -> Optional[date]:
            if not date_str:
                return None
            return date.fromisoformat(date_str)
        
        return cls(
            landlord_id=landlord_id,
            start_date=parse_date(start_date),
            end_date=parse_date(end_date),
        )


class CreateLandlordSchema(BaseModel):
    user_id: int
    company_name: str
    phone: str

    @classmethod    
    def as_form(
        cls,
        user_id: int = Form(...),
        company_name: str = Form(...),
        phone: str = Form(...),
    ):
        return cls(
            user_id=user_id,
            company_name=company_name,
            phone=phone
        )