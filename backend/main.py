from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
from parser import parse_reviews

app = FastAPI(
    title="Sentiment Guard API"
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

@app.post("/companies/", response_model=schemas.Company)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = crud.get_company_by_url(db, url=str(company.url))
    if db_company:
        raise HTTPException(status_code=400, detail="Компания с таким URL уже существует")

    return crud.create_company(db=db, company=company)

@app.post("/companies/{company_id}/fetch-reviews/")
def fetch_reviews(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()

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
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Компания не найдена")

    return db_company