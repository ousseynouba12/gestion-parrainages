from pydantic import BaseModel
from datetime import date
from typing import Literal

class ElecteurTemporaireValideBase(BaseModel):
    numElecteur: str
    numCIN: str
    nom: str
    prenom: str
    dateNaissance: date
    lieuNaissance: str
    sexe: Literal["M", "F"]
    bureauVote: str
    idTentative: int

class ElecteurTemporaireValide(ElecteurTemporaireValideBase):
    class Config:
        from_attributes = True

