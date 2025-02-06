import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
# from app.schemas.models import 


SECRET_KEY = os.getenv("JWT_SECRET", "key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# hashing pass
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# User DB here:
# Example:
fake_db = {
    "abc@eg.com":{
        "email": "abc@eg.com",
        "hashed_password": pwd_context.hash("password123"),
    },
}


# Pass Verifier:
def verify_password(plain_pass, hashed_pass):
    return pwd_context.verify(plain_pass, hashed_pass)

# 
def get_password_hash(password):
    return pwd_context.hash(password)


# User Authentication Func:
def authenticate_user(email:str, password:str):
    user = fake_db.get(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user


# JWT Access Token Create:
def create_access_token(data:dict, expires_delta: timedelta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# Get user from JWT Token
def get_current_user(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return {"email": email}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")