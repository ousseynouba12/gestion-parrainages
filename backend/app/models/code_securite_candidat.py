# app/models/code_securite_candidat.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class CodeSecuriteCandidat(Base):
    __tablename__ = "CodeSecuriteCandidat"

    idCode = Column(Integer, primary_key=True, autoincrement=True)
    numCandidat = Column(String(20), ForeignKey("Candidat.numElecteur"), nullable=False)
    code = Column(String(6), nullable=False)
    dateEnvoi = Column(DateTime, nullable=False, default=datetime.utcnow)

