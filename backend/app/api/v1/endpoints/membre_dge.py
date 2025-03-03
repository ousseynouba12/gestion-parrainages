from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core.database import get_db
from app.models.membre_dge import MembreDGE
from app.schemas.membre_dge import MembreDGECreation, MembreDGEOUT
import traceback

router = APIRouter()

# Configurer le contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=MembreDGEOUT)
def create_membre(membre: MembreDGECreation, db: Session = Depends(get_db)):
    try:
        # Vérifier si un membre avec le même email ou numéro de téléphone existe déjà
        existing_membre = db.query(MembreDGE).filter(
            (MembreDGE.email == membre.email) | (MembreDGE.telephone == membre.telephone)
        ).first()

        if existing_membre:
            raise HTTPException(
                status_code=400,
                detail="Un membre avec cet email ou ce numéro de téléphone existe déjà."
            )

        # Créer le dictionnaire des données du membre
        membre_data = membre.dict()

        # Hasher le mot de passe avant de le stocker
        if 'password' in membre_data:
            password = membre_data.pop('password')  # Retirer le mot de passe en clair
            hashed_password = pwd_context.hash(password)
            membre_data['password'] = hashed_password

        # Créer l'instance du membre
        db_membre = MembreDGE(**membre_data)
        
        db.add(db_membre)
        db.commit()
        db.refresh(db_membre)
        return db_membre
    
    except HTTPException:
        raise  # Relancer l'exception HTTP directement
    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la création : {str(e)}"
        )

@router.get("/", response_model=list[MembreDGEOUT])
def get_membres(db: Session = Depends(get_db)):
    return db.query(MembreDGE).all()

# Route pour vérifier les identifiants
@router.post("/login")
def login_membre(email: str, password: str, db: Session = Depends(get_db)):
    membre = db.query(MembreDGE).filter(MembreDGE.email == email).first()
    if not membre:
        raise HTTPException(
            status_code=401,
            detail="Email incorrect"
        )
    
    if not pwd_context.verify(password, membre.password):
        raise HTTPException(
            status_code=401,
            detail="Mot de passe incorrect"
        )
    
    return {"message": "Connexion réussie"}

