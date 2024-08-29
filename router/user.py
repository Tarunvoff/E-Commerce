from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from schemas.schemas import UserSchema, UserLoginSchema
from database import model
from database.database import get_db
from utility import utility
from auth.auth import verify_token, create_access_token

user_router = APIRouter(
    tags=["User"],
    prefix="/api/user"
)

# Create User - Redirect to login on success
@user_router.post("/create", response_class=RedirectResponse)
async def create_user(
    user: UserSchema,
    db: Session = Depends(get_db)
):
    existing_user = db.query(model.User).filter(
        (model.User.username == user.username) |
        (model.User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    hashed_password = utility.get_password_hashed(user.password)
    new_user = model.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_active=user.is_active,
        mobno=user.mobno
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

    return RedirectResponse(url="/api/login", status_code=status.HTTP_302_FOUND)

# POST Login - Accept UserLoginSchema and return JSON with access token
@user_router.post("/login", response_class=JSONResponse)
async def login(
    user_data: UserLoginSchema,
    db: Session = Depends(get_db)
):
    user = db.query(model.User).filter(model.User.username == user_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
        )

    if not utility.verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return JSONResponse(content={"access_token": access_token})

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
