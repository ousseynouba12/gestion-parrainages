from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")  # Test de la connexion à la base de données
        return {"message": "Connexion réussie ! 🎉"}
    except Exception as e:
        return {"error": str(e)}
