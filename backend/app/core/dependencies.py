from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pymongo.database import Database
from typing import Dict, Any

from app.core.config import settings
from app.database.mongodb import get_database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user via JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
        
    # Convert ObjectId to string for the id field
    user["_id"] = str(user["_id"])
    return user
