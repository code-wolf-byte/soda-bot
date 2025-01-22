from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(String)
    time = Column(String)
    location = Column(String)
    description = Column(String)
    prioritized = Column(Boolean)
    uuid = Column(String)