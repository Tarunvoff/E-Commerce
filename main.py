from fastapi import FastAPI
from database import model
from database.database import engine
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime,timedelta
from jose import JWTError,jwt
from passlib.context import CryptContext
from database.database import get_db



app=FastAPI()


model.Base.metadata.create_all(engine)


SECRET_KEY="40454c3e"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto",)
oauth_2_scheme=OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hashed(password):
    return pwd_context.hash(password)


from router.router import router
app.include_router(router)
