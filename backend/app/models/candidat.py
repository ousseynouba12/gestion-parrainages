from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Candidat(Base):
    __tablename__ = "candidat"

    numElecteur = Column(String(20), ForeignKey("electeur.numElecteur"), primary_key=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)
    partiPolitique = Column(String(100))
    slogan = Column(Text)
    photo = Column(Text)  # URL ou chemin de la photo
    couleur1 = Column(String(10))
    couleur2 = Column(String(10))
    couleur3 = Column(String(10))
    urlInfo = Column(Text)

    electeur = relationship("Electeur")

