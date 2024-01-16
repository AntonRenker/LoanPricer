from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models
import requests
import xml.etree.ElementTree as ET

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
