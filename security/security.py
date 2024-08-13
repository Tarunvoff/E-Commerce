from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import model
from database.database import get_db
from database.model import Token
from schemas.schemas import TokenSchema
# Secret key to encode the JWT tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()



# def create_access_token(data: dict, db: Session, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now() + expires_delta
#     else:
#         expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Store the token in the database
def create_access_token(data: dict,db: Session, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    token = Token(token=encoded_jwt, user_id=data["sub"])
    db.add(token)
    try:
        db.commit()
        db.refresh(token)  # Ensures that the token object is refreshed with the ID from the database
    except Exception as e:
        db.rollback()  # Rolls back the transaction in case of an error
        raise HTTPException(status_code=500, detail=f"Token could not be stored: {str(e)}")
    finally:
        inserted_token = db.query(Token).filter(Token.token == encoded_jwt).first()
        if not inserted_token:
            raise HTTPException(status_code=500, detail="Token was not inserted into the database")

    return encoded_jwt



def verify_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        exp = payload.get("exp")
        if username is None or exp is None:
            raise HTTPException(status_code=403, detail="Invalid token")

        if datetime.now() > datetime.fromtimestamp(exp):
            db.query(Token).filter(Token.token == credentials.credentials).delete()
            db.commit()
            raise HTTPException(status_code=403, detail="Token has expired")
        
        token = db.query(Token).filter(Token.token == credentials.credentials).first()
        if token is None:
            raise HTTPException(status_code=403, detail="Token not found in database")
        
        return username
    
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
