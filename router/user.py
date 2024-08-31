from fastapi import APIRouter, HTTPException, Depends, status,Request, Form
from fastapi.responses import JSONResponse, RedirectResponse,HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from typing import List

from schemas.schemas import UserSchema, UserLoginSchema
from database import model
from database.database import get_db
from utility import utility
from auth.auth import verify_token, create_access_token
from auth.auth import get_current_user


user_router = APIRouter(
    tags=["User"],
    prefix="/api/user"
)
templates = Jinja2Templates(directory="templates")

# Create User - Redirect to login on success
@user_router.get("/create-user", response_class=HTMLResponse)
async def create_user_page(request: Request):
    return templates.TemplateResponse("createuser.html", {"request": request})

@user_router.post("/create-user", response_class=RedirectResponse)
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    mobno: str = Form(...),
    is_active: bool = Form(True),
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
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    return 'added'
   

@user_router.get("/login", response_class=HTMLResponse)
async def get_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@user_router.post("/login")
async def login(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.username == user_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username")

    if not utility.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = create_access_token(data={"sub": str(user.id)})
    # return JSONResponse(content={"access_token": access_token})
    return RedirectResponse(url="/api/user/home",status_code=status.HTTP_302_FOUND)
@user_router.get("/protected-endpoint", response_class=HTMLResponse)
async def protected_endpoint(
    request: Request, 
    user_id: int = Depends(verify_token),  # Directly get user_id from the dependency
    db: Session = Depends(get_db)
):
    # Use the user_id directly returned from verify_token
    user = db.query(model.User).filter(model.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Render the protected page with the user information
    return templates.TemplateResponse("protected.html", {"request": request, "user": user})

@user_router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_db)):
    products = db.query(model.Products).all()
    return templates.TemplateResponse("home.html", {"request": request, "products": products})


# Read Single User - Return JSON
@user_router.get("/read", response_model=UserSchema)
async def read_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

# Read All Users - Return JSON
@user_router.get("/read-all", response_model=List[UserSchema])
async def read_all_users(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    try:
        users = db.query(model.User).all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

# Update User - Return JSON
@user_router.put("/update", response_model=UserSchema)
async def update_user(
    updated_user: UserSchema,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.username = updated_user.username
    user.email = updated_user.email
    user.is_active = updated_user.is_active
    user.mobno = updated_user.mobno
    user.password = utility.get_password_hashed(updated_user.password)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    
    return user

# Delete User - Return JSON
@user_router.delete("/delete", response_class=JSONResponse)
async def delete_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    try:
        db.delete(user)
        db.commit()
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
