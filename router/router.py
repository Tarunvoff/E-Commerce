from fastapi import APIRouter, status, UploadFile, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

#from main import app
from schemas import schemas
from utility import utility
from database import model
from database.database import get_db

router = APIRouter(
    tags=["API"],
    prefix="/api"
)


# CREATING A USER
@router.post("/create-user")
def create_user(request: schemas.UserSchema, db: Session = Depends(get_db)):
    print(request.json()) 
    hashed_password = utility.get_password_hashed(request.password)
    new_user = model.User(
        username=request.username,
        email=request.email,
        is_active=request.is_active,
        mobno=request.mobno,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User created successfully"}
    )

