from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from app.core.database import Base

# Modèle pour la table des paramètres
class Parametres(Base):
    __tablename__ = "Parametres"
    id = Column(Integer, primary_key=True, autoincrement=True)
    etatUploadElecteurs = Column(Boolean, default=False)
