from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text  # Ajoutez cet import
from app.db.database import get_db

router = APIRouter()

@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Utilisez text() pour la requête SQL
        result = db.execute(text("SELECT 1"))
        return {"message": "Connexion réussie ! 🎉"}
    except Exception as e:
        return {"error": str(e)}
