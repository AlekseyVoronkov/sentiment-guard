from sqlalchemy.orm import Session
import models, schemas

def get_company_by_url(db: Session, url: str):
    return db.query(models.Company).filter(models.Company.url == url).first()

def create_company(db: Session, company: schemas.CompanyCreate):
    db_company = models.Company(name=company.name, url=str(company.url))
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
