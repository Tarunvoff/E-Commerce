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
class ProductSchema(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    stock: int

    class Config:
        from_attributes = True
        
class TokenSchema(BaseModel):
    token: str
    user_id: int

    class Config:
        from_attributes = True






