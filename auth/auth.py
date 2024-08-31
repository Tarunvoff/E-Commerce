from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jwt import PyJWTError

from database import model
from database import database
from configuration import config

# Secret key to encode the JWT tokens
SECRET_KEY = config.app_config['auth']['SECRET_KEY']
ALGORITHM = config.app_config['auth']['algorithm']
ACCESS_TOKEN_EXPIRE_MINUTES = config.app_config['auth']['ACCESS_TOKEN_EXPIRE_MINUTES']

security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


exp = 30


def verify_token(authorization: str = Depends(oauth2_scheme)) -> int:
    try:
        # Log the incoming authorization header
        print(f"Authorization Header Received: {authorization}")

        # if not isinstance(authorization, str):
            # raise ValueError("Token is not a string.")

        # Attempt to split the header into type and token
        try:
            token_type, token = authorization.split(" ", 1)  # Avoiding split error by specifying maxsplit
            print(f"Token Type: {token_type}, Token: {token}")
        except ValueError as e:
            print(f"Error splitting token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed authorization header. Expected format: 'Bearer <token>'",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_type.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected 'Bearer'.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode the token and verify its payload
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"Decoded Payload: {payload}")
        except jwt.ExpiredSignatureError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTClaimsError as e:
            print(f"JWT Claims Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError as e:
            print(f"JWT Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("User ID not found in token.")

        print(f"Verified User ID: {user_id}")
        return int(user_id)

    except Exception as e:
        print(f"Error in token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> model.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(model.User).filter(model.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


