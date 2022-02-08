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


class PlanetRequest(BaseModel):
    id: Optional[int] = None
    name: str
    climates: str
    diameter: str
    population: str
    films: Optional[List[int]]

    class Config:
        orm_mode = True
