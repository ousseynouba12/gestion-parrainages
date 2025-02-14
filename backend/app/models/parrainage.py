from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.core.database import Base

class Parrainage(Base):
    __tablename__ = "parrainage"

    idParrainage = Column(Integer, primary_key=True, autoincrement=True)
    numElecteur = Column(String(20), ForeignKey("parrain.numElecteur"), nullable=False)
    numCandidat = Column(String(20), ForeignKey("candidat.numElecteur"), nullable=False)
    codeValidation = Column(String(6), nullable=False)
    dateParrainage = Column(DateTime, nullable=False)

