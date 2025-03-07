from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.core.database import Base
from sqlalchemy.orm import relationship


class Parrainage(Base):
    __tablename__ = "Parrainage"

    idParrainage = Column(Integer, primary_key=True, autoincrement=True)
    numElecteur = Column(String(20), ForeignKey("Parrain.numElecteur"), nullable=False)
    numCandidat = Column(String(20), ForeignKey("Candidat.numElecteur"), nullable=False)
    dateParrainage = Column(DateTime, nullable=False)

    candidat = relationship("Candidat", back_populates="parrainages")
    parrain = relationship("Parrain", back_populates="parrainages")
