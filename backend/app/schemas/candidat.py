from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CandidatBase(BaseModel):
    numElecteur: str
    email: EmailStr
    telephone: str
    partiPolitique: Optional[str] = None
    slogan: Optional[str] = None
    photo: Optional[str] = None
    #couleur1: Optional[str] = None
    #couleur2: Optional[str] = None
    #couleur3: Optional[str] = None
    urlInfo: Optional[str] = None

class CandidatCreate(CandidatBase):
    pass

class CandidatUpdate(BaseModel):
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    partiPolitique: Optional[str] = None
    slogan: Optional[str] = None
    photo: Optional[str] = None
    couleur1: Optional[str] = None
    couleur2: Optional[str] = None
    couleur3: Optional[str] = None
    urlInfo: Optional[str] = None

class CandidatOut(CandidatBase):
    numElecteur: str
    email: EmailStr
    telephone: str
    partiPolitique: Optional[str] = None
    slogan: Optional[str] = None
    photo: Optional[str] = None
    nbrParrainages: int
    
    class Config:
        from_attributes = True

class CandidatList(BaseModel):
    numElecteur: str
    partiPolitique: Optional[str]
    nbrParrainages: int
    
    class Config:
        from_attributes = True
