# app/models/audit_log.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "AuditLog"

    idAudit = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    dateAction = Column(DateTime, nullable=False, default=datetime.utcnow)

