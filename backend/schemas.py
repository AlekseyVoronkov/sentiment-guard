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

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    reviews: List[Review] = []

    class Config:
        orm_mode = True