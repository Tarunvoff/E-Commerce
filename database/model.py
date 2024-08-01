from database.database import Base
from sqlalchemy import (Column,String,Boolean,Integer,UniqueConstraint,DateTime,Enum)
from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint('email'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False) 
    email = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)  
    mobno = Column(String, nullable=False)
    password = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)


    