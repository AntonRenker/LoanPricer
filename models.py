from sqlalchemy import Column, Float, String
from database import Base


class Euribor(Base):
    __tablename__ = "Euribor"

    TimePeriod = Column(String, primary_key=True, index=True)
    ObsVal = Column(Float)
    BbkDiff = Column(Float)
    BbkDiffY = Column(Float)