from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from app.core.database import Base

class FichierElectoral(Base):
    __tablename__ = "fichier_electoral"

    idFichier = Column(Integer, primary_key=True, autoincrement=True)
    checksum = Column(String(64), nullable=False)  # SHA256
    dateUpload = Column(DateTime, nullable=False)
    idMembre = Column(Integer, ForeignKey("membre_dge.idMembre"), nullable=False)
    etatValidation = Column(Boolean, default=False)

