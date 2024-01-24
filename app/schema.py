from pydantic import BaseModel

class Euribor(BaseModel):
    TimePeriod: str
    ObsVal: float
    BbkDiff: float
    BbkDiffY: float

class Rating(BaseModel):
    Issuer: str
    LegalEntityIdentifier: str
    Rating: str
    RatingActionDate: str
    RatingAgency: str