from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
from passlib.context import CryptContext

# Créer un contexte de cryptage pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class MembreDGE(Base):
    __tablename__ = "Membre_dge"
    
    idMembre = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)
    role = Column(Enum("ADMIN", "MEMBRE", name="role_enum"), nullable=False, default="MEMBRE")
    password = Column(String(255), nullable=False)  # Pour stocker le mot de passe hashé

