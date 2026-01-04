from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List, Generic, TypeVar

#create a schema for user
class UserCreate(BaseModel):
    name: str
    email: EmailStr

#Create a schema for user response
class UserResponse(BaseModel): 
    id: int
    name: str
    email: EmailStr 

    class Config:
        from_attributes = True

# Optional schema for updating user
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None   

#Pagination schema
T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool
    data: List[T]




    