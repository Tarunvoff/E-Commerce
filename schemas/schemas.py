from pydantic import BaseModel, Field
from typing import List,Optional
from datetime import datetime

from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    email: str
    is_active: bool = True
    mobno: str
    password: str

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    price: float
    stock: int
    image_url: Optional[str] = None

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

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class CartItem(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True

class CartCreate(BaseModel):
    product_id: int
    quantity: int

class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: List[OrderItemSchema]

class OrderSchema(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemSchema]

    class Config:
        from_attributes = True


# ------------------------------------------------------>previous<-------------------------------------------------------------------------

        
# class TokenSchema(BaseModel):
#     token: str
#     user_id: int

#     class Config:
#         from_attributes = True






