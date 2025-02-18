from pydantic import BaseModel
from datetime import datetime

class AuditLogBase(BaseModel):
    utilisateur: str
    action: str
    dateAction: datetime

class AuditLog(AuditLogBase):
    idAudit: int

    class Config:
        from_attributes = True

