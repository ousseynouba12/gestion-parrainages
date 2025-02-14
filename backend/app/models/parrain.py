from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Parrain(Base):
    __tablename__ = "parrain"

    numElecteur = Column(String(20), ForeignKey("electeur.numElecteur"), primary_key=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)
    codeAuthentification = Column(String(6), nullable=False)

    electeur = relationship("Electeur")

