# app/schemas/tentative_upload.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TentativeUploadCreate(BaseModel):
    idFichier: int
    ip: str
    clefUtilisee: str
    resultat: bool

class TentativeUploadDB(TentativeUploadCreate):
    idTentative: int
    dateTentative: datetime

    class Config:
        from_attribute = True