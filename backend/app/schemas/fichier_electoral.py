# app/schemas/fichier_electoral.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FichierElectoralBase(BaseModel):
    checksum: str

class FichierElectoralCreate(FichierElectoralBase):
    cheminFichier: str

class FichierElectoralDB(FichierElectoralBase):
    idFichier: int
    dateUpload: datetime
    idMembre: int
    etatValidation: bool
    cheminFichier: str
    dateValidation: Optional[datetime] = None
    idMembreValidation: Optional[int] = None

    class Config:
        from_attribute = True
