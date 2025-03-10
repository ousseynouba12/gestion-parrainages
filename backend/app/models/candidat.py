# app/models/candidat.py
from sqlalchemy import Column, String, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Candidat(Base):
    __tablename__ = "Candidat"

    numElecteur = Column(String(20), ForeignKey("Electeur.numElecteur"), primary_key=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)
    partiPolitique = Column(String(100))
    slogan = Column(Text)
    photo = Column(Text)
    couleur1 = Column(String(10))
    couleur2 = Column(String(10))
    couleur3 = Column(String(10))
    urlInfo = Column(Text)
    nbrParrainages = Column(Integer, default=0)
    dateCreation = Column(DateTime, nullable=False, default=datetime.utcnow)
    dateDerniereModification = Column(DateTime, onupdate=datetime.utcnow)
    # Relation avec Electeur
    electeur = relationship("Electeur", back_populates="candidat")
    
    # Relations spécifiques à Candidat
    codes_securite = relationship("CodeSecuriteCandidat", back_populates="candidat", 
                                 order_by="desc(CodeSecuriteCandidat.dateEnvoi)", 
                                 cascade="all, delete-orphan")
    parrainages = relationship("Parrainage", back_populates="candidat", 
                               cascade="all, delete-orphan")