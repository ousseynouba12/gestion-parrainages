from sqlalchemy import Column, String, Date, Enum
from app.core.database import Base

class Electeur(Base):
    __tablename__ = "Electeur"

    numElecteur = Column(String(20), primary_key=True)
    numCIN = Column(String(20), unique=True, nullable=False, index=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    dateNaissance = Column(Date, nullable=False)
    lieuNaissance = Column(String(100), nullable=False)
    sexe = Column(Enum("M", "F", name="sexe_enum"), nullable=False)
    bureauVote = Column(String(100), nullable=False)

