from typing import Optional, List

from datetime import date
from pydantic import BaseModel


class FilmRequest(BaseModel):
    id: Optional[int] = None
    title: str
    release_date: date
    planets: Optional[List[int]] = []

    class Config:
        orm_mode = True

class FilmUpdateRequest(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    release_date: Optional[date] = None
    planets: Optional[List[int]] = None

    class Config:
        orm_mode = True

class PlanetRequest(BaseModel):
    id: Optional[int] = None
    name: str
    climates: Optional[str] = None
    diameter: Optional[str] = None
    population: Optional[str] = None
    films: Optional[List[int]] = []

    class Config:
        orm_mode = True

class PlanetUpdateRequest(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    climates: Optional[str] = None
    diameter: Optional[str] = None
    population: Optional[str] = None
    films: Optional[List[int]] = None

    class Config:
        orm_mode = True
