from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ReviewBase(BaseModel):
    author: str
    text: str
    date: str
    rating: int
    sentiment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True

class CompanyBase(BaseModel):
    name: str
    url: HttpUrl
    address: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    address: Optional[str] = None 
    owner_id: int
    reviews: List[Review] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str  

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True