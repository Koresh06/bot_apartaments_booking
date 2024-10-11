from typing import Optional, Union
from pydantic import BaseModel
from datetime import date
from fastapi import Form


class StatisticsDateSchema(BaseModel):
    start_date: Optional[Union[date, None]] = None  
    end_date: Optional[Union[date, None]] = None 

    @classmethod
    def as_form(
        cls,
        start_date: Optional[str] = Form(None), 
        end_date: Optional[str] = Form(None), 
    ):
        def parse_date(date_str: Optional[str]) -> Optional[date]:
            if not date_str:
                return None
            return date.fromisoformat(date_str)
        
        return cls(
            start_date=parse_date(start_date),
            end_date=parse_date(end_date),
        )
