from database.database import Base
from sqlalchemy import (
    Column, String, Boolean, Integer, UniqueConstraint, DateTime, Enum,func
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



    