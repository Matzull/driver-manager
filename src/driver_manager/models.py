from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(String, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class DriverHistory(Base):
    __tablename__ = "driver_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    driver_id = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
