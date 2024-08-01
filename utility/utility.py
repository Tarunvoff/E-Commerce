from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm,O
from pydantic import BaseModel
from datetime import datetime,timedelta
from schemas import User
from jose import JWTError,jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from schemas import UserInDb
from schemas import TokenData

SECRET_KEY="40454c3e"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto",)
oauth_2_scheme=OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hashed(password):
    return pwd_context.hash(password)

def get_user(db,username:str):
    if username in  db:
        user_data=db[username]
        return UserInDb(**user_data)
    

def Authenticate_user(db,username:str,password:str):
    user=get_user(db,username)
    if not user:
        return False
    if not verify_password(password,user.hashed_password):
      return False 
    return user


def create_access_token(data:dict,expires_delta : timedelta):
    to_encode=data.copy()
    if expires_delta:
        expire =datetime.now()+expires_delta
    else:
        expire=datetime.now()+timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt




async def get_current_user(token: str = Depends(oauth_2_scheme)) -> User:
    try:
        payload= jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        Cred_Exception=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        username:str=payload.get("sub")
        if username is None:
            raise Cred_Exception
        token_data=TokenData(username=username)

    except JWTError:
        raise Cred_Exception
    user=get_user(username=token_data.username)
    if user is None:
        raise Cred_Exception
    return user


