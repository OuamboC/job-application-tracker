# 1. Standard library
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

# 2. Third party
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import select

# 3. Local imports
from database import SessionDep
from models import TokenData, User

load_dotenv()  # loads .env file
SECRET_KEY = os.getenv("SECRET_KEY")  # reads SECRET_KEY from .env
ALGORITHM = "HS256"  # algorithm used to sign the token
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # token expires after 30 minutes


# recommended() automatically picks the strongest hashing algorithm
password_hash = PasswordHash.recommended()

# pre-computed hash used when user doesn't exist, prevents timing attacks
DUMMY_HASH = password_hash.hash("dummypassword")

# tells FastAPI where the login endpoint is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")


# checks if plain password matches the hashed one stored in DB
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

# hashes a plain password before storing it in DB
def get_password_hash(password):
    return password_hash.hash(password)

# checks username exists and password is correct, returns user or False
def authenticate_user(session, username: str, password: str):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        verify_password(password, DUMMY_HASH)  # prevents timing attacks
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# creates a JWT token with expiry time and signs it with SECRET_KEY
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# extracts token from request and returns the current logged in user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == token_data.username)).first()
    if user is None:
        raise credentials_exception
    return user

# Update the dependencies
async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code = 400, detail = "Inactive user")
    return current_user










