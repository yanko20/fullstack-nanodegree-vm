import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class BikeType(Base):
    __tablename__ = 'bike_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class BikePart(Base):
    __tablename__ = 'bike_part'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    bike_type_id = Column(Integer, ForeignKey('bike_type.id'))
    bike_type = relationship(BikeType)


engine = create_engine('sqlite:///bikeparts.db')

Base.metadata.create_all(engine)
