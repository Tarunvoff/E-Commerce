from fastapi import APIRouter, Depends, HTTPException,status,Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.model import Order, OrderItem, Products, Cart
from schemas.schemas import OrderSchema, OrderCreate
from database.database import get_db
from auth.auth import verify_token
from typing import List
from fastapi.templating import Jinja2Templates

order_router = APIRouter(
    tags=["Order"],
    prefix="/order"
)
templates = Jinja2Templates(directory="templates")

@order_router.post("/create", response_model=OrderSchema)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        item = order.item
        product = db.query(Products).filter(Products.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")
        
        total_price = product.price * item.quantity

        order_item = OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )

        new_order = Order(
            user_id=user_id,
            total_price=total_price,
            items=[order_item]
        )
        
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        ) from e
    

    
@order_router.get("/{id}", response_model=OrderSchema)
async def get_order(
    id: int, 
    db: Session = Depends(get_db), 
    user_id: int = Depends(verify_token)
):
    try:
        order = db.query(Order).filter(Order.id == id, Order.user_id == user_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return order

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the order."
        ) from e

    except Exception as e:
        # Handle any other general exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        ) from e
    

@order_router.get("/orders", response_model=List[OrderSchema])
async def get_all_orders(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).all()
        
        if not orders:
            raise HTTPException(status_code=404, detail="No orders found")

        return orders

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching orders."
        ) from e

    except Exception as e:
        # Handle any other general exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        ) from e

@order_router.put("/{id}", response_model=OrderSchema)
async def update_order(
    id: int,
    order_update: OrderSchema,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        order = db.query(Order).filter(Order.id == id, Order.user_id == user_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update fields if provided
        if order_update.total_price is not None:
            order.total_price = order_update.total_price
        if order_update.created_at is not None:
            order.created_at = order_update.created_at

        db.commit()
        db.refresh(order)
        return order

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the order."
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        ) from e
    
@order_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        order = db.query(Order).filter(Order.id == id, Order.user_id == user_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        db.delete(order)
        db.commit()
        return {"detail": "Order deleted successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the order."
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        ) from e
@order_router.get("/view", response_class=HTMLResponse)
async def view_orders_page(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).all()
        return templates.TemplateResponse("orders.html", {"request": request, "orders": orders})
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders"
        ) from e
