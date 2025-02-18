from pydantic import BaseModel, EmailStr
from typing import Literal,Optional

class MembreDGEBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: str
    role: Literal["ADMIN", "MEMBRE"]

class MembreDGECreation(MembreDGEBase):
    pass  # Le champ idMembre étant une clé primaire auto-incrémentée, il ne doit pas être fourni lors de la création
				    #Pydantic exige par défaut tous les champs sauf s'ils sont explicitement marqués comme optionnels

class MembreDGEOUT(MembreDGEBase):
    idMembre: int

    class Config:
        from_attributes = True

