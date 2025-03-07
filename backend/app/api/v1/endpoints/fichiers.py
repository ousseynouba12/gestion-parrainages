# app/api/v1/endpoints/fichiers.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.schemas.fichier_electoral import FichierElectoralCreate, FichierElectoralOut
from app.models.fichier_electoral import FichierElectoral
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=FichierElectoralOut)
def upload_fichier(fichier: UploadFile = File(...), db: Session = Depends(get_db)):
    # Ici, vous devez calculer le checksum du fichier (ex. SHA256) et stocker le fichier
    checksum = "calculated-checksum"  # Remplacer par le calcul réel
    fichier_data = FichierElectoral(checksum=checksum, idMembre=1)  # idMembre à récupérer selon le contexte
    db.add(fichier_data)
    db.commit()
    db.refresh(fichier_data)
    return fichier_data

