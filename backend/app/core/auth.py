import uuid
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import get_settings
from ..models.database import get_db
from ..models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
settings = get_settings()
SECRET_KEY = settings.secret_key if hasattr(settings, 'secret_key') else "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'access_token_expire_minutes', 30)

# Security schemes
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError as e:
        return None


def generate_api_key() -> str:
    """Generate a new API key."""
    return f"sb_{uuid.uuid4().hex}"


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username/email and password."""
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is null or invalid
    if not credentials.credentials or credentials.credentials == "null" or credentials.credentials == "undefined":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is null or undefined. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_user(db: Session, email: str, username: str, password: str, full_name: str = None) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user = User(
        id=f"user_{uuid.uuid4().hex[:8]}",
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        api_key=generate_api_key()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 