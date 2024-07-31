from fastapi import APIRouter,status,UploadFile,Depends
from fastapi.responses import JSONResponse
from database.database import get_db
# from model.model import task
from sqlalchemy.orm import Session
from main import app
from schemas.schemas import user
# from schemas.schemas import taskschema
# from model.model import task
# from schemas.schemas import responsetask
from model.model import User
router = APIRouter(
    tags=["API"],
    prefix="/api"
)
#CREATING A USER 
@router.post("/creating user")
def create_user(request:user,db:Session=Depends(get_db)):
    new_user = User(
        Username=request.username,
        email=request.email,
        password=request.password
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(status_code=status.HTTP_201_CREATED,content={"message": "User created successfully"})
