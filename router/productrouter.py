from fastapi import (
    APIRouter, status, Depends,
    HTTPException
)
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from schemas import schemas
from database import model
from database.database import get_db
from security.security import verify_token

# Router for Product Management
product_router = APIRouter(
    tags=["Products"],
    prefix="/products"
)

@product_router.post("/add", response_model=schemas.ProductSchema)
async def add_product(
    product: schemas.ProductCreate,  # Expecting JSON payload
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        new_product = model.Products(
            name=product.name, 
            description=product.description, 
            price=product.price, 
            image_url=product.image_url, 
            stock=product.stock
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@product_router.get("/", response_model=list[schemas.ProductSchema])
async def read_products(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        products = db.query(model.Products).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@product_router.get("/{id}", response_model=schemas.ProductSchema)
async def read_product(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    product = db.query(model.Products).filter(model.Products.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@product_router.put("/{id}", response_model=schemas.ProductSchema)
async def update_product(
    id: int,
    product: schemas.ProductUpdate,  # Expecting JSON payload
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    existing_product = db.query(model.Products).filter(model.Products.id == id).first()
    
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        existing_product.name = product.name
        existing_product.description = product.description
        existing_product.price = product.price
        existing_product.stock = product.stock
        existing_product.image_url = product.image_url

        db.commit()
        db.refresh(existing_product)
        return existing_product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@product_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    product = db.query(model.Products).filter(model.Products.id == id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        db.delete(product)
        db.commit()
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

