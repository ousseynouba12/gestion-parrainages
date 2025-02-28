from sqlalchemy import Column, ForeignKey, String, Date, Enum, Text, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.models.electeur import Electeur



class Candidat(Electeur):
    __tablename__ = "Candidat"

    # Clé primaire héritée
    numElecteur = Column(String(20), ForeignKey("Electeur.numElecteur"), primary_key=True)

    # Informations de contact
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)

    # Informations de la candidature
    partiPolitique = Column(String(100))
    slogan = Column(Text)
    photo = Column(Text)
    couleur1 = Column(String(10))
    #couleur2 = Column(String(10))
    couleur3 = Column(String(10))
    urlInfo = Column(Text)

    # Statistiques
    nbrParrainages = Column(Integer, default=0)

    # Dates
    dateCreation = Column(DateTime, nullable=False, default=datetime.utcnow)
    dateDerniereModification = Column(DateTime, onupdate=datetime.utcnow)

    # Relations
    codes_securite = relationship("CodeSecuriteCandidat", back_populates="candidat", order_by="desc(CodeSecuriteCandidat.dateEnvoi)",  cascade="all, delete-orphan")
    parrainages = relationship("Parrainage", back_populates="candidat",  cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'candidat'
    }
