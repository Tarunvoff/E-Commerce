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
        print(authorization)

        if not isinstance(authorization, str):
            raise ValueError("Token is not a string.")
        
        token_type, token = authorization.split(" ")
        
        if token_type.lower() != "bearer":
            raise ValueError("Invalid token type.")

        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is empty",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("User ID not found in token.")

        return int(user_id)

    except jwt.ExpiredSignatureError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except IndexError as e:
        print(f"Error in token verification (IndexError): {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is malformed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError as e:
        print(f"Error in token verification (PyJWTError): {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
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


