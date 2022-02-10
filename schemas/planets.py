from typing import Optional, List

from pydantic import BaseModel, validator


class PlanetRequest(BaseModel):
    name: str
    climates: Optional[str] = None
    diameter: Optional[float] = None
    population: Optional[int] = None
    films: Optional[List[int]] = []

    @validator('diameter')
    def diameter_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('must be positive')
        return v

    @validator('population')
    def population_must_be_positive_or_zero(cls, v):
        if v is not None and v < 0:
            raise ValueError('must be positive or zero')
        return v

    class Config:
        orm_mode = True

class PlanetUpdateRequest(BaseModel):
    name: Optional[str] = None
    climates: Optional[str] = None
    diameter: Optional[float] = None
    population: Optional[int] = None
    films: Optional[List[int]] = None

    @validator('diameter')
    def diameter_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('must be positive')
        return v

    @validator('population')
    def population_must_be_positive_or_zero(cls, v):
        if v is not None and v < 0:
            raise ValueError('must be positive or zero')
        return v

    class Config:
        orm_mode = True
        
class PlanetResponse(BaseModel):
    id: int
    name: str
    climates: Optional[str] = None
    diameter: Optional[float] = None
    population: Optional[int] = None
    films: List[int]

    class Config:
        orm_mode = True
