from fastapi import (
    APIRouter, status, UploadFile, Depends,
    HTTPException, Request, Form
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

    #return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("user_created.html", {"request": request, "username": username})


#LOGIN 
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
    
    # Redirect to home page on successful login
    return templates.TemplateResponse("welcome.html", {"request": request})
    

@router.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request, username: str):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": username})
