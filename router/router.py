from fastapi import (
    APIRouter, status, UploadFile, Depends,
    HTTPException, Request, Form,Query
)
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from typing import Optional


from schemas import schemas
from utility import utility
from database import model
from database.database import get_db
from database.model import Products
from security.security import verify_token
from security.security import create_access_token
from schemas.schemas import TokenSchema


router = APIRouter(
    tags=["API"],
    prefix="/api"
)

templates = Jinja2Templates(directory="templates")


# CREATING A USER
@router.get("/create-user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})


@router.post("/create-user", response_class=HTMLResponse)
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    is_active: bool = Form(True),
    mobno: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    existing_user = db.query(model.User).filter(
        (model.User.username == username) |
        (model.User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    hashed_password = utility.get_password_hashed(password)
    new_user = model.User(
        username=username,
        email=email,
        password=hashed_password,
        is_active=is_active,
        mobno=mobno
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/api/login", status_code=status.HTTP_302_FOUND)

    
    #return templates.TemplateResponse("user_created.html", {"request": request, "username": username})


#LOGIN 
# 
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Retrieve user from the database
    user = db.query(model.User).filter(model.User.username == username).first()

    # Check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
        )

    # Verify the password
    if not utility.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    # Create an access token
    access_token = create_access_token(data={"sub": user.id}, db=db)
    # access_token = create_access_token(data={"sub": user.id},db=db)
    
    # Optionally, you could set the token in a cookie or return it in the response
    # Here, I am returning it as a JSON response
    response = RedirectResponse(url="/api/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

    return response

@router.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request, username: str):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": username})


# ADD PRODUCT ROUTER
@router.get("/add-product", response_class=HTMLResponse)
async def create_product_form(request: Request):
    return templates.TemplateResponse("addproduct.html", {"request": request})


@router.post("/add-product", response_class=HTMLResponse)
async def add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    image_url: str = Form(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)  # Get the user ID from the token
):
    try:
        # Create a new product instance
        new_product = Products(
            name=name, 
            description=description, 
            price=price, 
            image_url=image_url, 
            stock=stock
        )
        # Add the new product to the database
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        # Return success template
        return templates.TemplateResponse("product_added.html", {"request": request, "product": new_product})
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/products", response_class=HTMLResponse)
def read_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(Products).all()
    return templates.TemplateResponse("product.html", {"request": request, "products": products})


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Products).all()  
    return templates.TemplateResponse("home.html", {"request": request, "products": products})

# #update the features
# @router.update("/update-product/{{id}}", response_class=HTMLResponse)
# async def update_product_form(request: Request, id: int, db: Session = Depends(get_db)):
#     product = db.query(Products).filter(Products.id == id).first()
#     return templates.TemplateResponse("updateproduct.html", {"request": request, "product": product})

#update
@router.get("/update-product", response_class=HTMLResponse)
async def update_product_form(request: Request, id: int, db: Session = Depends(get_db)):
    # Check if ID is provided - This is technically redundant since `id` is a path parameter
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Product ID is required"})
    
    # Query the database for the product with the given ID
    product = db.query(Products).filter(Products.id == id).first()
    
    # Return an error if the product is not found
    if not product:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    
    # Render the form with the product details
    return templates.TemplateResponse("updateproduct.html", {"request": request, "product": product})


@router.post("/update-product", response_class=HTMLResponse)
async def update_product(
    request: Request,
    id: int = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    image_url: str = Form(...),
    db: Session = Depends(get_db)
):
    # Query the database for the product with the given ID
    product = db.query(Products).filter(Products.id == id).first()
    
    # If the product is found, update its details
    if product:
        product.name = name
        product.description = description
        product.price = price
        product.stock = quantity
        product.image_url = image_url

        db.commit()
        db.refresh(product)
        
        # Render the success template
        return templates.TemplateResponse("product_added.html", {"request": request, "product": product})
    
    

    return JSONResponse(status_code=404, content={"detail": "Product not found"})
@router.get("/delete-product", response_class=HTMLResponse)
async def delete_product_form(request: Request, id: int, db: Session = Depends(get_db)):
    if not id:
        return JSONResponse(status_code=400, content={"detail": "Product ID is required"})
    
    
    product = db.query(Products).filter(Products.id == id).first()
    
    if not product:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    
    
    return templates.TemplateResponse("delproduct.html", {"request": request, "product": product})
   
    
 
@router.post("/delete-product")
async def delete_product(id: int, db: Session = Depends(get_db)):
    # Fetch the product from the database
    product = db.query(Products).filter(Products.id == id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete the product
    db.delete(product)
    db.commit()
    
    # Redirect to a success page or homepage
    return RedirectResponse(url="/api/home", status_code=302)











