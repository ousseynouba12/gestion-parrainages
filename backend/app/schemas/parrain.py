# app/schemas/parrain.py
from pydantic import BaseModel
from datetime import date

class ParrainBase(BaseModel):
    numElecteur: str
    email: str
    telephone: str
    codeAuthentification: str

class ParrainCreate(ParrainBase):
    pass

class Parrain(ParrainBase):
    nom: str
    prenom: str
    dateNaissance: date
    lieuNaissance: str
    sexe: str
    bureauVote: str

    class Config:
        from_attribute = True