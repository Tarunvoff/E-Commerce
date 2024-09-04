from fastapi import (
    APIRouter, HTTPException, status, Depends,Form,Request
)
from fastapi.responses import JSONResponse,HTMLResponse,RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates


from schemas import schemas
from database.model import Products
from database import model
from database.database import get_db
from auth.auth import verify_token

# Router for Product Management
product_router = APIRouter(
    tags=["Products"],
    prefix="/products"
)
templates = Jinja2Templates(directory="templates")
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@product_router.get("/views", response_model=list[schemas.ProductSchema])
async def read_products(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        products = db.query(model.Products).all()
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@product_router.get("/{id}", response_model=schemas.ProductSchema)
async def read_product(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        product = db.query(model.Products).filter(model.Products.id == id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@product_router.put("/{id}", response_model=schemas.ProductSchema)
async def update_product(
    id: int,
    product: schemas.ProductUpdate,  # Expecting JSON payload
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        existing_product = db.query(model.Products).filter(model.Products.id == id).first()
        
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@product_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        product = db.query(model.Products).filter(model.Products.id == id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        db.delete(product)
        db.commit()
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    


# Render the "Add Product" page
@product_router.get("/add-product", response_class=HTMLResponse)
async def add_product_page(request: Request):
    return templates.TemplateResponse("addproduct.html", {"request": request})

# Handle form submission to add a new product
@product_router.post("/add-product", response_class=HTMLResponse)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    image_url: str = Form(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    # Check if the product already exists by name
    print(user_id)
    existing_product = db.query(Products).filter(Products.name == name).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists."
        )

    # Create a new product instance
    new_product = Products(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url or ""
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        # Redirect to a page (e.g., product list) after successful creation
        return RedirectResponse(url="/api/products/views", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
@product_router.get("/products/update-product/{product_id}", response_class=HTMLResponse)
async def update_product_page(request: Request, product_id: int, db: Session = Depends(get_db),_: int = Depends(verify_token)):
    # Retrieve the product from the database
    product = db.query(model.Products).filter(model.Products.id == product_id).first()

    # Handle if the product does not exist
    if not product:
        return HTMLResponse("Product not found", status_code=404)
    
    # Render the product data in the HTML form
    return templates.TemplateResponse("updateproduct.html", {"request": request, "product": product})