from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import Date
from database import Base


class Film(Base):
    __tablename__ = 'film'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, unique=True)
    release_date = Column(Date)
