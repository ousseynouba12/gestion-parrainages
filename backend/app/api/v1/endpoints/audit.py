from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogBase, AuditLog

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[AuditLog])
def get_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()

