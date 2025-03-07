from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.auth import (
    authenticate_membre, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    get_current_membre, 
    verify_admin
)
from app.schemas.auth import Token, UserLogin, UserCreate
from app.models.membre_dge import MembreDGE
from app.core.auth import get_password_hash

router = APIRouter()

# 1️⃣ Route de connexion - Génère un jeton JWT après validation de l'email et du mot de passe
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    membre = authenticate_membre(db, form_data.username, form_data.password)
    if not membre:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Création du token d'accès
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": membre.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 2️⃣ Route pour récupérer les informations de l'utilisateur connecté
@router.get("/me")
def get_profile(membre: MembreDGE = Depends(get_current_membre)):
    return {
        "id": membre.idMembre,
        "email": membre.email,
        "role": membre.role
    }

# 3️⃣ Route pour récupérer tous les membres (seulement pour les admins)
@router.get("/membres", dependencies=[Depends(verify_admin)])
def get_membres(db: Session = Depends(get_db)):
    membres = db.query(MembreDGE).all()
    return membres

# 4️⃣ Route pour créer un membre (par un administrateur)
@router.post("/membres", dependencies=[Depends(verify_admin)])
def create_membre(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    membre = MembreDGE(email=user.email, password=hashed_password, role=user.role)
    db.add(membre)
    db.commit()
    db.refresh(membre)
    return membre

# 5️⃣ Route de déconnexion (pas nécessaire pour JWT mais permet d’invalider côté client)
@router.post("/logout")
def logout():
    return {"message": "Déconnexion réussie. Supprimez le token côté client."}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    membre = authenticate_membre(db, form_data.username, form_data.password)
    if not membre:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": membre.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}