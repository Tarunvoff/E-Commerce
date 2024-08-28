from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from schemas.schemas import UserSchema  # Assuming your schema is in the `schemas` module
from schemas.schemas import UserLoginSchema
from database import model

from database.database import get_db
from utility import utility
from auth.auth import verify_token
from auth.auth import create_access_token

user_router = APIRouter(
    tags=["User"],
    prefix="/api/user"
)

# Create User - Redirect to login on success
@user_router.post("/create", response_class=RedirectResponse)
async def create_user(user: UserSchema, db: Session = Depends(get_db)):
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

#POST Login - Accept UserSchema and return JSON with access token
@user_router.post("/login", response_class=JSONResponse)
async def login(
    user_data: UserLoginSchema,  # Now using UserLoginSchema
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


# @user_router.post("/login", response_class=JSONResponse)
# async def login(
#     user_data: UserSchema,
#     db: Session = Depends(get_db)
# ):
#     # Retrieve user from the database
#     user = db.query(model.User).filter(model.User.username == user_data.username).first()

#     # Check if the user exists
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username",
#         )

#     # Verify the password
#     if not utility.verify_password(user_data.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect password",
#         )
    
#     # Create an access token
#     access_token = create_access_token(data={"sub": str(user.id)})

#     # Return the access token in a JSON response
#     return JSONResponse(content={"access_token": access_token})

# Read Single User - Return JSON
@user_router.get("/read/{user_id}", response_model=UserSchema)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
     
    
    return user

# Read All Users - Return JSON
@user_router.get("/read-all", response_model=List[UserSchema])
async def read_all_users(db: Session = Depends(get_db)):
    users = db.query(model.User).all()
    return users

# Update User - Return JSON
@user_router.put("/update/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, updated_user: UserSchema, db: Session = Depends(get_db)):
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
@user_router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    
    return "user is deleted"
