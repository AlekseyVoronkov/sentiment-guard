from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import os
from dotenv import load_dotenv
from typing import List

import crud, models, schemas
from database import SessionLocal, engine
from parser import parse_reviews
from auth import create_access_token, verify_password, get_current_user 

load_dotenv()

app = FastAPI(
    title="Sentiment Guard API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"message": "Бэк живет и передаёт привет."}

@app.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@app.post("/auth/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/companies/", response_model=List[schemas.Company])
def read_companies(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    companies = db.query(models.Company).filter(
        models.Company.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return companies

@app.post("/companies/", response_model=schemas.Company)
def create_company(
    company: schemas.CompanyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_company = crud.get_company_by_url(db, str(company.url), current_user)
    if db_company:
        raise HTTPException(status_code=400, detail="Компания с таким URL уже существует")

    return crud.create_company(db=db, company=company, user=current_user)

@app.post("/companies/{company_id}/fetch-reviews/")
def fetch_reviews(company_id: int, 
                  db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)
                  ):

    db_company = db.query(models.Company).filter(models.Company.id == company_id, 
                                                 models.Company.owner_id == current_user.id).first()

    if db_company is None:
        raise HTTPException(status_code=404, detail="Компания не найдена")

    final_url = str(db_company.url)
    if "/maps/org/" in final_url and "reviews" not in final_url and "?" not in final_url:
        final_url = final_url.rstrip("/") + "/reviews/"

    print(f"Итоговый URL для парсера: {final_url}")

    reviews_data = parse_reviews(final_url)

    saved_reviews_count = 0
    skipped_reviews_count = 0

    for review in reviews_data:
        existing_review = crud.get_review_by_content(
            db=db,
            company_id=company_id,
            author=review['author'],
            text=review['text'],
            date=review['date']
        )

        if not existing_review:
            review_schema = schemas.ReviewCreate(**review)
            crud.create_company_review(db=db, review=review_schema, company_id=company_id)
            saved_reviews_count += 1
        else:
            skipped_reviews_count += 1

    return {
        "message": "Парсинг завершен.",
        "saved_new_reviews": saved_reviews_count,
        "skipped_duplicates": skipped_reviews_count
    }

@app.get("/companies/{company_id}", response_model=schemas.Company)
def read_company(company_id: int, 
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)
                 ):
    
    db_company = db.query(models.Company).filter(models.Company.id == company_id, 
                                                 models.Company.owner_id == current_user.id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Компания не найдена")

    return db_company
