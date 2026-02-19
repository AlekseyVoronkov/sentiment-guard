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

def get_company_by_name(db: Session, name: str, user_id: int):
    return db.query(models.Company).filter(
        models.Company.name == name, 
        models.Company.owner_id == user_id
    ).first()

def create_company(db: Session, company: schemas.CompanyCreate, user_id: int):
    db_company = models.Company(
        name=company.name, 
        url_yandex=str(company.url_yandex) if company.url_yandex else None,
        url_2gis=str(company.url_2gis) if company.url_2gis else None,
        owner_id=user_id
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def delete_company(db: Session, company_id: int, address: str):
    if not address: return

    company = db.query(models.Company).filter(models.Company.id == company_id).first()

    if company and not company.address:
        company.address = address
        db.commit()
        db.refresh(company)

    return company

def update_company_address(db: Session, company_id: int, address: str):
    if not address:
        return
        
    company = db.query(models.Company).filter(models.Company.id == company_id).first()

    if company:
        company.address = address
        db.commit()
        db.refresh(company)
    return company

def create_company_review(db: Session, review: schemas.ReviewCreate, company_id: int):
    db_review = models.Review(**review.model_dump(), company_id=company_id)
    db.add(db_review)
    db.commit()
    return db_review

def get_review_by_content(db: Session, company_id: int, author: str, text: str, date: str, source: str):
    return db.query(models.Review).filter(
        models.Review.company_id == company_id,
        models.Review.author == author,
        models.Review.text == text,
        models.Review.date == date,
        models.Review.source == source
    ).first()
