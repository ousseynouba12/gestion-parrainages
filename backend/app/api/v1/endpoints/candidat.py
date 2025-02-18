from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random, string
from typing import List
from app.core.database import get_db
from app.models.candidat import Candidat
from app.models.code_securite_candidat import CodeSecuriteCandidat
from app.schemas.candidat import CandidatCreate, CandidatOut, CandidatUpdate, CandidatList, CandidatBase
from app.schemas.code_securite_candidat import CodeSecuriteCandidatBase, CodeSecuriteCandidatOut

router = APIRouter()

def generate_code() -> str:
    """Génère un code aléatoire de 6 caractères"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ------------------------- CRÉER UN CANDIDAT -------------------------
@router.post("/", response_model=CandidatOut)
def create_candidat(candidat: CandidatCreate, db: Session = Depends(get_db)):
    """Créer un nouveau candidat et générer automatiquement un code de sécurité"""

    # Vérifier si le candidat existe déjà
    if db.query(Candidat).filter(Candidat.numElecteur == candidat.numElecteur).first():
        raise HTTPException(status_code=400, detail="Ce candidat existe déjà.")

    # Création du candidat
    db_candidat = Candidat(
        **candidat.model_dump(),
        dateCreation=datetime.utcnow(),
        dateDerniereModification=datetime.utcnow()
    )
    db.add(db_candidat)
    db.commit()

    # Générer et associer un code de sécurité
    new_code = CodeSecuriteCandidat(
        numCandidat=candidat.numElecteur,
        code=generate_code(),
        dateEnvoi=datetime.utcnow(),
        estActif=True
    )
    db.add(new_code)
    db.commit()
    db.refresh(db_candidat)

    return db_candidat

# ------------------------- OBTENIR TOUS LES CANDIDATS -------------------------
@router.get("/", response_model=List[CandidatList])
def get_all_candidats(db: Session = Depends(get_db)):
    """Retourne la liste de tous les candidats"""
    return db.query(Candidat).all()

# ------------------------- OBTENIR UN CANDIDAT -------------------------
@router.get("/{numElecteur}", response_model=CandidatBase)
def get_candidat(numElecteur: str, db: Session = Depends(get_db)):
    """Récupère un candidat avec son dernier code de sécurité actif"""
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numElecteur).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")

    # Récupérer le dernier code actif
    code_actif = db.query(CodeSecuriteCandidat).filter(
        CodeSecuriteCandidat.numCandidat == numElecteur,
        CodeSecuriteCandidat.estActif == True
    ).order_by(CodeSecuriteCandidat.dateEnvoi.desc()).first()

    return {
        **candidat.__dict__,
        "codeSecu": code_actif.code if code_actif else None
    }

# ------------------------- METTRE À JOUR UN CANDIDAT -------------------------
@router.put("/{numElecteur}", response_model=CandidatOut)
def update_candidat(numElecteur: str, candidat_update: CandidatUpdate, db: Session = Depends(get_db)):
    """Mise à jour des informations du candidat"""
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numElecteur).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")
    
    # Vérifie si l'email ou le téléphone sont modifiés
    contact_modified = (
        (candidat_update.email and candidat_update.email != candidat.email) or
        (candidat_update.telephone and candidat_update.telephone != candidat.telephone)
    )

    # Mise à jour des informations
    for key, value in candidat_update.model_dump(exclude_unset=True).items():
        setattr(candidat, key, value)

    candidat.dateDerniereModification = datetime.utcnow()
    db.commit()
    db.refresh(candidat)
    
    # Si les informations de contact sont modifiées, générer un nouveau code
    if contact_modified:
        regenerate_password(numElecteur, db)

    return candidat

# ------------------------- SUPPRIMER UN CANDIDAT -------------------------
@router.delete("/{numElecteur}")
def delete_candidat(numElecteur: str, db: Session = Depends(get_db)):
    """Supprime un candidat"""
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numElecteur).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")
    print(f"Suppression du candidat : {candidat.numElecteur}")
    db.delete(candidat)
    db.commit()
    return {"message": "Candidat supprimé avec succès."}

# ------------------------- GÉNÉRER UN NOUVEAU CODE DE SÉCURITÉ -------------------------
@router.post("/{numElecteur}/generer_mdp", response_model=CodeSecuriteCandidatOut)
def regenerate_password(numElecteur: str, db: Session = Depends(get_db)):
    """
    Génère un nouveau mot de passe sécurisé pour un candidat.
    - Désactive l'ancien code
    - Génère un nouveau code sécurisé
    - Met à jour la date de dernière modification du candidat
    """

    # Vérifier que le candidat existe
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numElecteur).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")

    # Désactiver l’ancien code actif
    db.query(CodeSecuriteCandidat).filter(
        CodeSecuriteCandidat.numCandidat == numElecteur,
        CodeSecuriteCandidat.estActif == True
    ).update({"estActif": False})

    # Générer un nouveau code de sécurité
    new_code = generate_code()

    # Ajouter un nouveau code
    new_code_entry = CodeSecuriteCandidat(
        numCandidat=numElecteur,
        code=new_code,
        dateEnvoi=datetime.utcnow(),
        estActif=True
    )
    db.add(new_code_entry)

    # Mettre à jour la date de dernière modification
    candidat.dateDerniereModification = datetime.utcnow()
    db.commit()
    db.refresh(new_code_entry)

    return new_code_entry


# ------------------------- SUSPENDRE UN CANDIDAT -------------------------
@router.put("/{numElecteur}/suspendre", response_model=CandidatOut)
def suspend_candidat(numElecteur: str, db: Session = Depends(get_db)):
    """Suspend un candidat en mettant son statut à inactif"""
    
    # Récupérer le candidat
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numElecteur).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")
    
    code_actif = db.query(CodeSecuriteCandidat).filter(
        CodeSecuriteCandidat.numCandidat == numElecteur,
        CodeSecuriteCandidat.estActif == True
    ).order_by(CodeSecuriteCandidat.dateEnvoi.desc()).first()
    
    if code_actif:
        code_actif.estActif = False
        db.commit()
        db.refresh(code_actif)
    
    db.commit()
    db.refresh(candidat)
    
    return candidat

