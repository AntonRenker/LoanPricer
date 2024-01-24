from sqlalchemy import Column, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Euribor(Base):
    __tablename__ = "Euribor"

    TimePeriod = Column(String, primary_key=True, index=True)
    ObsVal = Column(Float)
    BbkDiff = Column(Float)
    BbkDiffY = Column(Float)

class Rating(Base):
    __tablename__ = "Rating"

    Issuer = Column(String, primary_key=True, index=True)
    LegalEntityIdentifier = Column(String, primary_key=True, index=True)
    Rating = Column(String)
    RatingActionDate = Column(String)
    RatingAgency = Column(String)