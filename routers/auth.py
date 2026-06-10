# 1. Standard library
from datetime import timedelta                      
from typing import Annotated

# 2. Third party
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# 3. Local imports
from models import User, UserCreate, UserPublic, Token
from database import SessionDep
from auth.security import get_password_hash, create_access_token, authenticate_user, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()  # creates a mini app that gets plugged into the main app in main.py

# register a new user - hashes password before storing in DB
@router.post("/register", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    hashed_password = get_password_hash(user.password)  # hash before storing
    db_user = User.model_validate(user, update={"hashed_password": hashed_password})
    session.add(db_user)        # stage user to be saved
    session.commit()            # save to DB
    session.refresh(db_user)    # refresh with DB generated values (e.g: id)
    return db_user

# login endpoint - validates credentials and returns JWT token
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)  # check credentials
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},  # tells client to use Bearer token
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # set expiry time
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires  # sub = subject (username)
    )
    return Token(access_token=access_token, token_type="bearer")

# returns the current logged in user's profile - requires valid JWT token
@router.get("/users/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],  # injects current user
) -> User:
    return current_user