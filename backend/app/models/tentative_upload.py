from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Boolean
from app.core.database import Base

class TentativeUpload(Base):
    __tablename__ = "tentative_upload"

    idTentative = Column(Integer, primary_key=True, autoincrement=True)
    idFichier = Column(Integer, ForeignKey("fichier_electoral.idFichier"), nullable=False)
    dateTentative = Column(DateTime, nullable=False)
    ip = Column(String(45), nullable=False)
    clefUtilisee = Column(String(64), nullable=False)  # SHA256
    resultat = Column(Boolean, nullable=False)

