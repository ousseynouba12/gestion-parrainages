from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ParrainageBase(BaseModel):
    numElecteur: str
    numCandidat: str
    codeValidation: str
    dateParrainage: Optional[datetime] = datetime.utcnow()

class ParrainageOut(ParrainageBase):
    idParrainage: int

    class Config:
        from_attributes = True

