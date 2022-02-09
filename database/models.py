from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Date
from database.database import Base

class Association(Base):
    __tablename__ = 'association'
    film_id  = Column(ForeignKey('film.id'), primary_key=True)
    planet_id = Column(ForeignKey('planet.id'), primary_key=True)
    official = Column(Boolean, default=False)
    film = relationship("Film", back_populates="planets")
    planet = relationship("Planet", back_populates="films")

class Film(Base):
    __tablename__ = 'film'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, unique=True)
    release_date = Column(Date)
    official = Column(Boolean, default=False)
    planets = relationship("Association", back_populates="film")

class Planet(Base):
    __tablename__ = 'planet'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True)
    climates = Column(String, nullable=True)
    diameter = Column(Float, nullable=True)
    population = Column(Integer, nullable=True)
    official = Column(Boolean, default=False)
    films = relationship("Association", back_populates="planet")
