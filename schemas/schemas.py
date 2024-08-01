from pydantic import BaseModel
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    id:int
    Username:str
    email:str
    password:str
    is_active:bool = None
    mobno:str
    class Config:
        orm_mode=True
class UserInDB(User):
    hashed_password: str
     
            

