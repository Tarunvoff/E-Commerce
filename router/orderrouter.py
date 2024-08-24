from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.model import Order, OrderItem, Products, Cart
from schemas.schemas import OrderSchema, OrderCreate
from database.database import get_db
from security.security import verify_token
from typing import List

order_router = APIRouter(
    tags=["Order"],
    prefix="/order"
)

@order_router.post("/create", response_model=OrderSchema)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    total_price = 0
    items = []
    
    for item in order.items:
        product = db.query(Products).filter(Products.id == item.product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")
        
        total_price += product.price * item.quantity
        
        order_item = OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        items.append(order_item)

    new_order = Order(
        user_id=user_id,
        total_price=total_price,
        items=items
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@order_router.get("/{id}", response_model=OrderSchema)
async def get_order(id: int, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    order = db.query(Order).filter(Order.id == id, Order.user_id == user_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@order_router.get("/all", response_model=List[OrderSchema])
async def get_all_orders(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return orders
