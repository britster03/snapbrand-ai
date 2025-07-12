from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..core.auth import (
    authenticate_user,
    create_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..models.database import get_db
from ..models.user import User

router = APIRouter(prefix="/v1/auth", tags=["authentication"])


class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str = None
    is_active: bool
    is_premium: bool
    total_images_generated: int
    total_cost_spent: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    user = create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name
    )
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
async def login_json(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user with JSON payload and return access token."""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@router.get("/api-key")
async def get_api_key(current_user: User = Depends(get_current_active_user)):
    """Get current user's API key."""
    return {"api_key": current_user.api_key}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Refresh the current user's access token."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/validate")
async def validate_token(current_user: User = Depends(get_current_active_user)):
    """Validate the current token and return user info."""
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    } 