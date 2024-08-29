from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from database.model import Cart, Products
from database.database import get_db
from schemas.schemas import CartItem, CartCreate
from auth.auth import verify_token

cart_router = APIRouter(
    tags=["Cart"],
    prefix="/cart"
)

@cart_router.post("/add", response_model=CartItem)
async def add_to_cart(
    cart: CartCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        product = db.query(Products).filter(Products.id == cart.product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        new_cart_item = Cart(
            user_id=user_id,
            product_id=cart.product_id,
            quantity=cart.quantity
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        return new_cart_item

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        ) from e

@cart_router.get("/items", response_model=List[CartItem])
async def get_cart_items(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
        return cart_items

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart items"
        ) from e

@cart_router.delete("/remove/{id}")
async def remove_from_cart(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        cart_item = db.query(Cart).filter(Cart.id == id, Cart.user_id == user_id).first()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        db.delete(cart_item)
        db.commit()
        return {"detail": "Item removed from cart"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from cart"
        ) from e
