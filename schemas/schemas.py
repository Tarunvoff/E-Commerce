from pydantic import BaseModel
from typing import List

class user(BaseModel):
    id:int
    Username:str
    password:str
    email:str