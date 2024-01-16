from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models
import requests
import xml.etree.ElementTree as ET
from datetime import date

def clean_database(db: Session):
    try:
        # Assuming `Euribor` is the model representing the table you want to clean
        db.query(models.Euribor).delete()
        db.commit()
        return {"message": "Database cleaned successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cleaning database: {str(e)}")
    
def update_database(db: Session):
    download_url = 'https://www.bundesbank.de/statistic-rmi/StatisticDownload?tsId=BBIG1.M.D0.EUR.MMKT.EURIBOR.W01.AVE.MA&its_fileFormat=sdmx&mode=its'
    save_path = 'data/Euribor.xml'

    try:
        response = requests.get(download_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved at {save_path}")

        tree = ET.parse(save_path)
        root = tree.getroot()

        for child in root.iter():
            attributes = child.attrib
            if attributes.get('TIME_PERIOD'):
                time = attributes['TIME_PERIOD']
                # String to date (string format: YYYY-MM)
                time = date(int(time[:4]), int(time[5:]), 1)

                if not db.query(models.Euribor).filter(models.Euribor.TimePeriod == time).first():
                    db_entry = models.Euribor(
                        TimePeriod=time,
                        ObsVal=float(attributes.get('OBS_VALUE', 0)),
                        BbkDiff=float(attributes.get('BBK_DIFF', 0)),
                        BbkDiffY=float(attributes.get('BBK_DIFF_Y', 0))
                    )
                    
                    db.add(db_entry)
                    db.commit()
    except requests.RequestException as e:
        print(f"Error during data update: {str(e)}")

def get_entries_date(start_date: str, end_date: str, db: Session):
    try:
        start_date = date(int(start_date[:4]), int(start_date[5:]), 1)
        end_date = date(int(end_date[:4]), int(end_date[5:]), 1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format, should be 'YYYY-MM': {str(e)}")

    try:
        return db.query(models.Euribor).filter(models.Euribor.TimePeriod >= start_date, models.Euribor.TimePeriod <= end_date).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting entries from database: {str(e)}")
      
