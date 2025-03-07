from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from app.core.database import Base
from sqlalchemy.sql import func

class JournalActions(Base):
    __tablename__ = "Journal_actions"
    idAction = Column(Integer, primary_key=True, autoincrement=True)
    idMembre = Column(Integer, ForeignKey("Membre_dge.idMembre"), nullable=False)
    action = Column(String(1000), nullable=False)
    dateAction = Column(DateTime, default=func.now(), nullable=False)
    details = Column(String(4000), nullable=True)