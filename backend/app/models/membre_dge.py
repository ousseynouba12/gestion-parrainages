# app/models/membre_dge.py

from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base

class MembreDGE(Base):
    __tablename__ = "membre_dge"

    idMembre = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)
    role = Column(Enum("ADMIN", "MEMBRE", name="role_enum"), nullable=False, default="MEMBRE")

