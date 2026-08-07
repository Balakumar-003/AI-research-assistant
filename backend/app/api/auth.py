from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from typing import Dict, Any

from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.services.auth_service import register_user, authenticate_user
from app.database.mongodb import get_database
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Database = Depends(get_database)):
    """Register a new user."""
    return register_user(db, request)

@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Database = Depends(get_database)):
    """Authenticate user and return a JWT."""
    return authenticate_user(db, request)

@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user
