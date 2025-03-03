from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.fichier_electoral import FichierElectoral
from app.schemas.fichier_electoral import FichierElectoralBase, FichierElectoral

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FichierElectoral)
def upload_fichier(fichier: FichierElectoralBase, db: Session = Depends(get_db)):
    db_fichier = FichierElectoral(**fichier.dict())
    db.add(db_fichier)
    db.commit()
    db.refresh(db_fichier)
    return db_fichier

