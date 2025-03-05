from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from app.core.database import Base

class CodeSecuriteCandidat(Base):
    __tablename__ = "CodeSecuriteCandidat"
    
    idCode = Column(Integer, primary_key=True, autoincrement=True)
    numCandidat = Column(String(20), ForeignKey("Candidat.numElecteur"), nullable=False)
    code = Column(String(128), nullable=False)
    dateEnvoi = Column(DateTime, nullable=False, default=datetime.utcnow)    
    # Relation avec Candidat
    candidat = relationship("Candidat", back_populates="codes_securite")

