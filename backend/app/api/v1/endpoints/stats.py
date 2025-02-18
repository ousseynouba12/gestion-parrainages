# app/api/v1/endpoints/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/")
def get_stats(db: Session = Depends(get_db)):
    # Exemple simple de statistiques
    total_electeurs = db.execute("SELECT COUNT(*) FROM electeur").scalar()
    total_candidats = db.execute("SELECT COUNT(*) FROM candidat").scalar()
    total_parrainages = db.execute("SELECT COUNT(*) FROM parrainage").scalar()
    return {
        "total_electeurs": total_electeurs,
        "total_candidats": total_candidats,
        "total_parrainages": total_parrainages
    }

