from fastapi import APIRouter, Depends, HTTPException, status,Request,Form,Query
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from fastapi.templating import Jinja2Templates



from database.model import Cart, Products
from database.database import get_db
from schemas.schemas import CartItem, CartCreate
from auth.auth import verify_token

templates = Jinja2Templates(directory="templates")

cart_router = APIRouter(
    tags=["Cart"],
    prefix="/cart"
)

@cart_router.post("/cart/add", response_model=CartCreate)
async def add_to_cart(
    cart: CartCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        # Check if the product exists
        product = db.query(Products).filter(Products.id == cart.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create a new cart item
        new_cart_item = Cart(
            user_id=user_id,
            product_id=cart.product_id,
            quantity=cart.quantity,
            is_disabled=cart.is_disabled  # Make sure this value is correctly handled
        )
        
        # Add and commit the new cart item
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        return new_cart_item

    except SQLAlchemyError as e:
        db.rollback()
        # Log error if needed for debugging
        print(f"SQLAlchemy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        ) from e
    

@cart_router.get("/items", response_class=HTMLResponse)
async def get_cart_items_page(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
        return templates.TemplateResponse("carts.html", {"request": request, "cart_items": cart_items})
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

@cart_router.get("/cart", response_class=HTMLResponse)
async def view_cart(db: Session = Depends(get_db)):
    user_id = 1  # Fetch this from the user session or token
    cart_items = db.query(Cart).filter(Cart.user_id == user_id, Cart.is_disabled == False).all()

@cart_router.get("/view", response_class=HTMLResponse)
async def view_cart_page(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
        return templates.TemplateResponse("carts.html", {"request": request, "cart_items": cart_items})
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart items"
        ) from e
    