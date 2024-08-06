from database.database import Base
from sqlalchemy import (
    Column, String, Boolean, Integer, UniqueConstraint, DateTime, Enum,func,Float
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
class DefaultColumn(Base):
    __abstract__ = True
    __table_args__ = {'extend_existing': True}

    is_disabled = Column(Boolean, default=False, nullable=False)
    created_ts = Column(DateTime, default=func.now())
    updated_ts = Column(DateTime, default=func.now(), onupdate=func.now())

class User(DefaultColumn):
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

class Products(DefaultColumn):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint('name'),
        {'extend_existing': True}
    )
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)  
    image_url = Column(String, nullable=False)
    stock = Column(Integer, nullable=False)




    