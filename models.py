from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    cooking_time = Column(Integer)
    ingredients = Column(String)
    description = Column(String)
    views = Column(Integer, default=0)
