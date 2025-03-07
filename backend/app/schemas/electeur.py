from pydantic import BaseModel, Field
from datetime import date
from typing import Literal

class ElecteurBase(BaseModel):
    numElecteur: str = Field(..., min_length=8, max_length=20, description="Numéro unique de l'électeur")
    numCIN: str = Field(..., min_length=10, max_length=20, description="Numéro de Carte d'Identité Nationale")
    nom: str = Field(..., min_length=2, max_length=50, description="Nom de l'électeur")
    prenom: str = Field(..., min_length=2, max_length=50, description="Prénom de l'électeur")
    dateNaissance: date = Field(..., description="Date de naissance")
    lieuNaissance: str = Field(..., min_length=2, max_length=100, description="Lieu de naissance")
    sexe: Literal["M", "F"] = Field(..., description="Sexe de l'électeur (M/F)")
    bureauVote: str = Field(..., min_length=5, max_length=100, description="Bureau de vote assigné")

class ElecteurCreation(ElecteurBase):
    pass  # Identique au modèle de base

class ElecteurOut(ElecteurBase):
    class Config:
        from_attributes = True

