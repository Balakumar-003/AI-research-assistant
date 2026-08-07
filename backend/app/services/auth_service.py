from fastapi import HTTPException, status
from pymongo.database import Database

from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse
from app.models.user_model import create_user_document
from app.core.security import hash_password, verify_password, create_access_token

def register_user(db: Database, request: RegisterRequest) -> dict:
    """Business logic for registering a user."""
    # Check if email is unique
    existing_user = db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
        
    # Create the user document
    hashed_pwd = hash_password(request.password)
    user_doc = create_user_document(request.name, request.email, hashed_pwd)
    
    # Insert to DB
    db.users.insert_one(user_doc)
    
    return {"message": "User registered successfully"}

def authenticate_user(db: Database, request: LoginRequest) -> TokenResponse:
    """Business logic for authenticating a user and returning a JWT token."""
    user = db.users.find_one({"email": request.email})
    
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
        
    access_token = create_access_token(subject=user["email"])
    return TokenResponse(access_token=access_token, token_type="bearer")
