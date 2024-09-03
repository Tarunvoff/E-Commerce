from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, UniqueConstraint, DateTime, Enum, func, Float, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database.database import Base

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

    orders = relationship("Order", back_populates="user")
    carts = relationship("Cart", back_populates="user")


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

    orders = relationship("OrderItem", back_populates="product")
    carts = relationship("Cart", back_populates="product")


class Order(DefaultColumn):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class Cart(Base):
    __tablename__ = 'cart'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    is_disabled = Column(Boolean, nullable=False, default=False)  
    created_at = Column(DateTime, default=datetime.now)

    product = relationship("Products", back_populates="carts")
    user = relationship("User", back_populates="carts")


class OrderItem(DefaultColumn):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Products")








    