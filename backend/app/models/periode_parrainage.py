from sqlalchemy import Column, Integer, Date, Enum
from app.core.database import Base

class PeriodeParrainage(Base):
    __tablename__ = "periode_parrainage"

    idPeriode = Column(Integer, primary_key=True, autoincrement=True)
    dateDebut = Column(Date, nullable=False)
    dateFin = Column(Date, nullable=False)
    etat = Column(Enum("OUVERT", "FERMÉ", name="etat_periode_enum"), nullable=False, default="FERMÉ")

