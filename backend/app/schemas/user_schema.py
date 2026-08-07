from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    role: str
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "60d5ecb54f1e4a3b1c8e8d1a",
                "name": "John Doe",
                "email": "john@gmail.com",
                "role": "user"
            }
        }
