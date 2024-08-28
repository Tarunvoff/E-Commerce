from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from jwt import PyJWTError
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import model
from database.database import get_db
from configuration import config
from pydantic import BaseModel
# from database.model import Token
# from schemas.schemas import TokenSchema
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

# class TokenData(BaseModel):
#     user_id: int
   
exp=30
def verify_token(authorization: str = Depends(oauth2_scheme)) -> int:
    try:
        print(authorization)
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # if not authorization.startswith("Bearer "):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid authentication scheme",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )

        token = authorization
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is empty",
                headers={"WWW-Authenticate": "Bearer"},
            )
        #token regeneration
        
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # token_data = TokenData(**payloa
        user_id=payload.get("sub")

        # if datetime.fromtimestamp(exp) - datetime.now() < timedelta(minutes=5):
        #     new_token = create_access_token(data={"sub": user_id})
        #     response = JSONResponse(content={"access_token": new_token})
        #     response.headers["X-New-Token"] = new_token
        #     return response

        return int(user_id)
        # return token_data.user_id 

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





#                              --------- Previous Code----------------------
# def create_access_token(data: dict, db: Session, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now() + expires_delta
#     else:
#         expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Store the token in the database



# def create_access_token(data: dict,db: Session, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now() + expires_delta
#     else:
#         expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     # token = Token(token=encoded_jwt, user_id=data["sub"])
#     # db.add(token)
#     # try:
#     #     db.commit()
#     #     db.refresh(token)  # Ensures that the token object is refreshed with the ID from the database
#     # except Exception as e:
#     #     db.rollback()  # Rolls back the transaction in case of an error
#     #     raise HTTPException(status_code=500, detail=f"Token could not be stored: {str(e)}")
#     # finally:
#     #     inserted_token = db.query(Token).filter(Token.token == encoded_jwt).first()
#     #     if not inserted_token:
#     #         raise HTTPException(status_code=500, detail="Token was not inserted into the database")

#     return encoded_jwt

# second try -----------------------------------------------
# def verify_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         exp = payload.get("exp")
#         if username is None or exp is None:
#             raise HTTPException(status_code=403, detail="Invalid token")

#         if datetime.now() > datetime.fromtimestamp(exp):
#             db.query(Token).filter(Token.token == credentials.credentials).delete()
#             db.commit()
#             raise HTTPException(status_code=403, detail="Token has expired")
        
#         token = db.query(Token).filter(Token.token == credentials.credentials).first()
#         if token is None:
#             raise HTTPException(status_code=403, detail="Token not found in database")
        
#         return username
    
#     except JWTError:
#         raise HTTPException(status_code=403, detail="Could not validate credentials")
# ---------------------------------------------------- third try---------------------------------------------------
# def verify_token(authorization: str = Depends(oauth2_scheme)) -> int:
    # try:
    #     # Check if the authorization header starts with 'Bearer'
    #     if not authorization.startswith("Bearer "):
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Invalid authentication scheme",
    #             headers={"WWW-Authenticate": "Bearer"},
    #         )
        
    #     # Extract the token from the header
    #     token = authorization.split(" ")[1]  # This is where the index error can occur

    #     # Decode and verify the token
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #     token_data = TokenData(**payload)
    #     return token_data.user_id
    # except IndexError:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token format",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # except JWTError as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Could not validate credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # except Exception as e:
    #     print(f"Error in token verification: {e}")  # Debugging line
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Internal Server Error",
    #     )
