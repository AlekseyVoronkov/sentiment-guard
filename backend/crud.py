from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)

    db_user = models.User(email=user.email, password_hash=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_company_by_url(db: Session, url: str, user: models.User):
    return db.query(models.Company).filter(models.Company.url == url, models.Company.owner_id == user.id).first()

def create_company(db: Session, company: schemas.CompanyCreate, user: models.User):
    db_company = models.Company(name=company.name, url=str(company.url), owner_id=user.id)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def create_company_review(db: Session, review: schemas.ReviewCreate, company_id: int):
    db_review = models.Review(**review.model_dump(), company_id=company_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_review_by_content(db: Session, company_id: int, author: str, text: str, date: str):
    return db.query(models.Review).filter(
        models.Review.company_id == company_id,
        models.Review.author == author,
        models.Review.text == text,
        models.Review.date == date
    ).first()
