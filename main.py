from fastapi import FastAPI, HTTPException, Depends
import app.models as models
from app.database import get_db, create_tables
from sqlalchemy.orm import Session
from app.schema import Euribor
from database_operations import *

app = FastAPI()
create_tables()

@app.post("/update-euriobor")
async def update_data_base(db: Session = Depends(get_db)):
    update_euribor_database(db)
    return {"message": "Database updated"}

@app.post("/update-rating")
async def update_rating(db: Session = Depends(get_db)):
    update_rating_database(db)
    return {"message": "Database updated"}

@app.get("/get-euribor-entries-all")
async def read_api_all(db: Session = Depends(get_db)):
    return db.query(models.Euribor).all()

@app.get("/get-rating-entries-all")
async def read_api_all(db: Session = Depends(get_db)):
    return db.query(models.Rating).all()

@app.get("/get-rating-by-issuer/{issuer}")
async def read_api_issuer(issuer: str, db: Session = Depends(get_db)):
    return get_entries_by_issuer(issuer, db)

@app.get("/get-rating-by-entity-identifier/{entity_identifier}")
async def read_api_entity_identifier(entity_identifier: str, db: Session = Depends(get_db)):
    return get_entries_by_entity_identifier(entity_identifier, db)

@app.get("/get-euribor-entries/{start_date}/{end_date}")
async def read_api_date(start_date: str, end_date: str, db: Session = Depends(get_db)):
    return get_entries_date_euribor(start_date, end_date, db)

@app.delete("/clean-database")
async def clean_whole_database(db: Session = Depends(get_db)):
    return clean_database(db)
