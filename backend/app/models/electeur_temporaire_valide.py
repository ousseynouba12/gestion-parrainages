# app/models/electeur_temporaire_valide.py
from sqlalchemy import Column, String, Integer, ForeignKey, Date
from app.core.database import Base

class ElecteurTemporaireValide(Base):
    __tablename__ = "ElecteurTemporaireValide"

    numElecteur = Column(String(20), primary_key=True)
    numCIN = Column(String(20), nullable=False)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    dateNaissance = Column(Date, nullable=False)
    lieuNaissance = Column(String(100), nullable=False)
    sexe = Column(String(1), nullable=False)
    bureauVote = Column(String(100), nullable=False)
    idTentative = Column(Integer, ForeignKey("Tentative_upload.idTentative"), nullable=False)

