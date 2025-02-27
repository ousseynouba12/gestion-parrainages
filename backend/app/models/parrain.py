from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Parrain(Base):
    __tablename__ = "Parrain"

    numElecteur = Column(String(20), ForeignKey("Electeur.numElecteur"), primary_key=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)
    codeAuthentification = Column(String(6), nullable=False)

    electeur = relationship("Electeur")
    parrainages = relationship("Parrainage", back_populates="parrain")

