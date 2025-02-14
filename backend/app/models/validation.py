from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.core.database import Base
from datetime import datetime

class ValidationFichier(Base):
    __tablename__ = "validation_fichier"

    idValidation = Column(Integer, primary_key=True, autoincrement=True)
    idFichier = Column(Integer, ForeignKey("fichier_electoral.idFichier"), nullable=False)
    dateValidation = Column(DateTime, nullable=False, default=datetime.utcnow)
    resultat = Column(String(20), nullable=False)  # "validé" ou "rejeté"

