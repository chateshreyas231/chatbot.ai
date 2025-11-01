"""Authentication utilities."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db import get_database
from db.models import User
from config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    database = await get_database()
    user_doc = await database.users.find_one({"email": email})
    
    if user_doc is None:
        raise credentials_exception
    
    return User(**user_doc)


async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    database = await get_database()
    user_doc = await database.users.find_one({"email": email})
    
    if user_doc:
        return User(**user_doc)
    return None


async def create_user(email: str, name: str, aad_sub: Optional[str] = None) -> User:
    """Create a new user."""
    database = await get_database()
    
    # Check if user exists
    existing = await get_user_by_email(email)
    if existing:
        return existing
    
    user = User(
        email=email,
        name=name,
        aad_sub=aad_sub,
        role="user"
    )
    
    user_dict = user.model_dump(by_alias=True, exclude={"id"})
    result = await database.users.insert_one(user_dict)
    user.id = result.inserted_id
    
    return user


# Demo mode: Magic link authentication
async def create_magic_link_token(email: str) -> str:
    """Create magic link token for demo."""
    data = {"sub": email, "type": "magic_link"}
    expire = timedelta(minutes=15)
    return create_access_token(data, expires_delta=expire)


async def verify_magic_link_token(token: str) -> Optional[str]:
    """Verify magic link token."""
    try:
        payload = jwt.decode(token, settings.magic_link_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") == "magic_link":
            return payload.get("sub")
    except JWTError:
        pass
    return None

