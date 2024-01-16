from fastapi import FastAPI, HTTPException, Depends
import app.models as models
from app.database import get_db
from sqlalchemy.orm import Session
from app.schema import Euribor
from database_operations import *

app = FastAPI()

@app.get("/")
async def read_api(db: Session = Depends(get_db)):
    return db.query(models.Euribor).all()

@app.post("/clean-database")
async def clean_whole_database(db: Session = Depends(get_db)):
    return clean_database(db)

@app.post("/update-database")
async def update_data_base(db: Session = Depends(get_db)):
    update_database(db)