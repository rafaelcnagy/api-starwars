from typing import Optional, List

from datetime import date
from pydantic import BaseModel


class FilmRequest(BaseModel):
    id: Optional[int] = None
    title: str
    release_date: date
    planets: Optional[List[int]]

    class Config:
        orm_mode = True
