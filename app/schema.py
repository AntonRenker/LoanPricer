from pydantic import BaseModel

class Euribor(BaseModel):
    TimePeriod: str
    ObsVal: float
    BbkDiff: float
    BbkDiffY: float