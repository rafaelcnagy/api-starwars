from typing import Optional

from datetime import date
from pydantic import BaseModel

class FilmRequest(BaseModel):
    id: Optional[int] = None
    title: str
    release_date: date

    class Config:
        orm_mode = True
