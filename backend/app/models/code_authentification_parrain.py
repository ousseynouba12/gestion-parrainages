# app/models/code_authentification_parrain.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from datetime import datetime
from app.core.database import Base

class CodeAuthentificationParrain(Base):
    __tablename__ = "CodeValidationParrain"

    idCode = Column(Integer, primary_key=True, autoincrement=True)
    numParrain = Column(String(20), ForeignKey("Parrain.numElecteur"), nullable=False)
    code = Column(String(128), nullable=False)
    dateEnvoi = Column(DateTime, nullable=False, default=datetime.utcnow)
    est_actif= Column(Boolean, default=True)
