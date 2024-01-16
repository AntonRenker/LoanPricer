from fastapi import FastAPI, HTTPException, Depends
import app.models as models
from app.database import get_db
from sqlalchemy.orm import Session
from app.schema import Euribor
from database_operations import *

app = FastAPI()
@app.post("/")
async def root():
    return {"message": "API is running"}

@app.post("/update-database")
async def update_data_base(db: Session = Depends(get_db)):
    update_database(db)


@app.get("/get-entries-all")
async def read_api_all(db: Session = Depends(get_db)):
    return db.query(models.Euribor).all()

@app.get("/get-entries/{start_date}/{end_date}")
async def read_api_date(start_date: str, end_date: str, db: Session = Depends(get_db)):
    return get_entries_date(start_date, end_date, db)

@app.delete("/clean-database")
async def clean_whole_database(db: Session = Depends(get_db)):
    return clean_database(db)
