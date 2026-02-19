from pydantic import BaseModel, HttpUrl, model_validator
from typing import List, Optional
from datetime import datetime

class ReviewBase(BaseModel):
    author: str
    text: str
    date: str
    rating: int
    sentiment: Optional[str] = None
    source: str = 'yandex'

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True

class CompanyBase(BaseModel):
    name: str
    url_yandex: Optional[HttpUrl] = None
    url_2gis: Optional[HttpUrl] = None
    address: Optional[str] = None

class CompanyCreate(CompanyBase):
    @model_validator(mode='after')
    def check_at_least_one_url(self):
        if not self.url_yandex and not self.url_2gis:
            raise ValueError('Нужно указать хотя бы одну ссылку (Яндекс или 2ГИС)')
        return self
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