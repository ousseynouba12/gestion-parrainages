from pydantic import BaseModel
from datetime import date
from typing import Literal

class PeriodeParrainageBase(BaseModel):
    dateDebut: date
    dateFin: date
    etat: Literal["OUVERT", "FERMÉ"]

class PeriodeParrainage(PeriodeParrainageBase):
    idPeriode: int

    class Config:
        from_attributes = True

