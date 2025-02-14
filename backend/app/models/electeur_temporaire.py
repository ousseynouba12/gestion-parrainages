from sqlalchemy import Column, String, ForeignKey, Text
from app.core.database import Base

class ElecteurTemporaire(Base):
    __tablename__ = "electeur_temporaire"

    numElecteur = Column(String(20), primary_key=True)
    numCIN = Column(String(20), nullable=False)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    erreur = Column(Text, nullable=False)
    idTentative = Column(Integer, ForeignKey("tentative_upload.idTentative"), nullable=False)

