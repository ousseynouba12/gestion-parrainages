from pydantic import BaseModel
from datetime import datetime

class TentativeUploadBase(BaseModel):
    idFichier: int
    dateTentative: datetime
    idMembre: int
    ip: str
    clefUtilisee: str
    resultat: bool

class TentativeUploadCreation(TentativeUploadBase):
    pass

class TentativeUpload(TentativeUploadBase):
    idTentative: int

    class Config:
        from_attributes = True

