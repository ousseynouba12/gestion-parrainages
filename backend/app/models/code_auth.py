from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base

class CodeAuthentification(Base):
    __tablename__ = "code_auth"

    idCode = Column(Integer, primary_key=True, autoincrement=True)
    numParrain = Column(String(20), ForeignKey("parrain.numElecteur"), nullable=False)
    code = Column(String(6), nullable=False)
    dateEnvoi = Column(DateTime, nullable=False)

