from typing import Optional, List

from datetime import date
from pydantic import BaseModel


class FilmRequest(BaseModel):
    title: str
    release_date: date
    planets: Optional[List[int]] = []

    class Config:
        orm_mode = True

class FilmUpdateRequest(BaseModel):
    title: Optional[str] = None
    release_date: Optional[date] = None
    planets: Optional[List[int]] = None

    class Config:
        orm_mode = True

class FilmResponse(BaseModel):
    id: int
    title: str
    release_date: date
    planets: List[int]

    class Config:
        orm_mode = True
