from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class MembreDGECreation(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: str = Field(..., pattern=r'^\+?[0-9]{8,15}$')   # Validation du format téléphone
    role: str = "MEMBRE"
    password: str

class MembreDGEOUT(BaseModel):
    idMembre: int
    nom: str
    prenom: str
    email: str
    telephone: str
    role: str

    class Config:
        from_attributes = True
