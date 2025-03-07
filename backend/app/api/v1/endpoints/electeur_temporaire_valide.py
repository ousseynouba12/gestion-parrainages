from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.electeur_temporaire_valide import ElecteurTemporaireValide
from app.schemas.electeur_temporaire_valide import ElecteurTemporaireValideBase, ElecteurTemporaireValide

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[ElecteurTemporaireValide])
def get_electeurs(db: Session = Depends(get_db)):
    return db.query(ElecteurTemporaireValide).all()

