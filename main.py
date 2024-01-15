from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime
import xml.etree.ElementTree as ET
import requests

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Euribor(BaseModel):
    TimePeriod: datetime
    ObsVal: float
    BbkDiff: float
    BbkDiffY: float

@app.get("/{start_date}/{end_date}")
async def read_api(start_date: str, end_date: str, db: Session = Depends(get_db)):
    parsed_start_date = datetime.strptime(start_date, "%Y-%m")
    parsed_end_date = datetime.strptime(end_date, "%Y-%m")

    if parsed_start_date > parsed_end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    else:
        return db.query(models.Euribor).filter(models.Euribor.TimePeriod.between(start_date, end_date)).all()


@app.post("/")
async def update_data_base(db: Session = Depends(get_db)):
    # Replace 'link' with the actual download link
    download_url = 'https://www.bundesbank.de/statistic-rmi/StatisticDownload?tsId=BBIG1.M.D0.EUR.MMKT.EURIBOR.W01.AVE.MA&its_fileFormat=sdmx&mode=its'

    response = requests.get(download_url)
    save_path = 'data/Euribor.xml'

    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved at {save_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

    tree = ET.parse("data/Euribor.xml")
    root = tree.getroot()

    for child in root.iter():
        attributes = child.attrib
        if attributes:
            if 'TIME_PERIOD' in attributes.keys():
                time = datetime.strptime(attributes['TIME_PERIOD'], "%Y-%m")
                if not db.query(models.Euribor).filter(models.Euribor.TimePeriod == time).first():
                    db_entry = models.Euribor()
                    db_entry.TimePeriod = time
                    db_entry.ObsVal = float(attributes['OBS_VALUE'])
                    if 'BBK_DIFF' in attributes.keys():
                        db_entry.BbkDiff = float(attributes['BBK_DIFF'])
                    if 'BBK_DIFF_Y' in attributes.keys():
                        db_entry.BbkDiffY = float(attributes['BBK_DIFF_Y'])
                    
                    db.add(db_entry)
                    db.commit()

@app.delete("/{id}")
def delete_entry(id: str, db: Session = Depends(get_db)):
    time = datetime.strptime(id, "%Y-%m")
    db_entry = db.query(models.Euribor).filter(models.Euribor.Date == time)
    if db_entry is None:
        raise HTTPException(status_code=404, detail=f"{id} not found")
    db.query(models.Euribor).filter(models.Euribor.Date == id).delete()
    db.commit()
    return db_entry
