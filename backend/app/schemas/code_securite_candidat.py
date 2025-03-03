from pydantic import BaseModel
from datetime import datetime

class CodeSecuriteCandidatBase(BaseModel):
    numCandidat: str
    code: str

class CodeSecuriteCandidatCreate(CodeSecuriteCandidatBase):
    """Schéma pour créer un code de sécurité (généré automatiquement)"""
    pass

class CodeSecuriteCandidatOut(CodeSecuriteCandidatBase):
    """Schéma de sortie pour afficher les infos du code de sécurité"""
    idCode: int
    dateEnvoi: datetime
    estActif: bool

    class Config:
        from_attributes = True

