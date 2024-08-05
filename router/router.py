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

    return templates.TemplateResponse("user_created.html", {"request": request, "username": username})

# @router.post("/create-user")
# def create_user(request: schemas.UserSchema, db: Session = Depends(get_db)):
#     hashed_password = utility.get_password_hashed(request.password)
#     new_user = model.User(
#         username=request.username,
#         email=request.email,
#         is_active=request.is_active,
#         mobno=request.mobno,
#         password=hashed_password
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return JSONResponse(
#         status_code=status.HTTP_201_CREATED,
#         content={"message": "User created successfully"}
#     )
# END OF CREATING A USER



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
    #return RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)


@router.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request, username: str):
    return templates.TemplateResponse("welcome.html", {"request": request, "username": username})

# # Login method
# @router.get("/login", response_class=HTMLResponse)
# async def login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})


# @router.post("/login", response_class=HTMLResponse)
# async def login(
#     request: Request,
#     username: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(model.User).filter(model.User.username == username).first()
#     if not user :
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username "
#         )
#     if not not utility.verify_password(password, user.password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect Password"
#         )
    
#     return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


# @router.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("welcome.html", {"request": request})




# # Route to handle login logic
# @app.post("/login", response_class=HTMLResponse)
# async def login(
#     request: Request,
#     username: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(model.User).filter(model.User. username == username).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username"
#         )
#     if not verify_password(password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect password"
#         )
    
#     return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# # Route to render the welcome page
# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("welcome.html", {"request": request})