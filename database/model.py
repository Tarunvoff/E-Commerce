from database.database import Base
from sqlalchemy import (Column,String,Boolean,Integer,UniqueConstraint,DateTime,Enum)


class User(Base):
    __tablename__="user"
    __tableargs__=(
        UniqueConstraint('email'),
        {'extend_existing':True}
        )
    id = Column(Integer,primary_key=True,index=True)
    Username = Column(String,nullable=False)
    email = Column(String,nullable=False)
    is_active=Column(Boolean,nullable=False)
    password = Column(String,nullable=False)
    mobno = Column(String, nullable=False)

class UserInDB(User):
    hashed_password = Column(String, nullable=False)

    