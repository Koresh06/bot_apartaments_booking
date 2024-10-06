from typing import Optional, Union
from pydantic import BaseModel
from datetime import date
from fastapi import Form

class LandlordDateSchema(BaseModel):
    landlord_id: int
    start_date: Optional[Union[date, None]] = None  # поддержка строк и None
    end_date: Optional[Union[date, None]] = None    # поддержка строк и None

    @classmethod
    def as_form(
        cls,
        landlord_id: int = Form(...),
        start_date: Optional[str] = Form(None),  # строка по умолчанию
        end_date: Optional[str] = Form(None),    # строка по умолчанию
    ):
        # Преобразуем пустые строки в None
        def parse_date(date_str: Optional[str]) -> Optional[date]:
            if not date_str:
                return None
            return date.fromisoformat(date_str)
        
        return cls(
            landlord_id=landlord_id,
            start_date=parse_date(start_date),
            end_date=parse_date(end_date),
        )
