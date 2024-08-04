from pydantic import BaseModel
from typing import List


from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    email: str
    is_active: bool = True
    mobno: str
    password: str

    class Config:
        from_attributes = True




