from sqlalchemy import Column, Integer, Boolean, String, DateTime, Text, ForeignKey, desc
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    url_yandex = Column(String, nullable=True) 
    url_2gis = Column(String, nullable=True)

    address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    reviews = relationship("Review", back_populates="company", order_by="desc(Review.date)")
    owner = relationship("User", back_populates="companies")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String, index=True)
    text = Column(Text)
    date = Column(String)
    rating = Column(Integer)
    sentiment = Column(String, index=True, nullable=True)
    source = Column(String, index=True, default='yandex')
    
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="reviews")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)

    companies = relationship("Company", back_populates="owner")