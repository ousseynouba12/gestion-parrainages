from pydantic import BaseModel
from datetime import datetime

class FichierElectoralBase(BaseModel):
    checksum: str
    dateUpload: datetime
    idMembre: int
    etatValidation: bool

class FichierElectoralCreation(FichierElectoralBase):
    pass

class FichierElectoral(FichierElectoralBase):
    idFichier: int

    class Config:
        from_attributes = True

