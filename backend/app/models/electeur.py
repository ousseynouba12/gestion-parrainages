# app/models/electeur.py
from sqlalchemy import Column, String, Date, Enum, Text, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Electeur(Base):
    __tablename__ = "Electeur"

    numElecteur = Column(String(20), primary_key=True)
    numCIN = Column(String(20), unique=True, nullable=True, index=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    dateNaissance = Column(Date, nullable=False)
    lieuNaissance = Column(String(100), nullable=False)
    sexe = Column(Enum("M", "F", name="sexe_enum"), nullable=False)
    bureauVote = Column(String(100), nullable=False)
    
    # Relations (optionnel, si nécessaire)
    parrain = relationship("Parrain", back_populates="electeur", uselist=False)
    candidat = relationship("Candidat", back_populates="electeur", uselist=False)