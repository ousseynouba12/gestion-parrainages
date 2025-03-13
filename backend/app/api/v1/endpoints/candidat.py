from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload
from datetime import datetime
from typing import List
from app.core.database import get_db
from app.models.candidat import Candidat
from app.models.code_securite_candidat import CodeSecuriteCandidat
from app.schemas.candidat import CandidatCreate, CandidatOut, CandidatUpdate, CandidatList, CandidatBase
from app.schemas.code_securite_candidat import CodeSecuriteCandidatOut
from app.services.code_generator import code_generator_service

router = APIRouter()

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
    
    # Ajouter et committer pour s'assurer que le candidat est bien enregistré
    db.add(db_candidat)
    db.commit()
    db.refresh(db_candidat)
    
    # Candidat enregistré, maintenant gérer le code de sécurité
    try:
        # Un candidat se parraine lui-même à son enregistrement
        if hasattr(candidat, 'nbrParrainages'):
            candidat.nbrParrainages = 1
        
        # Générer et associer un code de sécurité, puis l'envoyer
        code_generator_service.create_security_code(db, candidat.numElecteur, send_notifications=True)
        print(f"Code de sécurité généré pour {candidat.numElecteur}")
    except Exception as e:
        # Continuer même si l'envoi échoue, mais logguer l'erreur
        print(f"Erreur lors de la génération ou l'envoi du code: {str(e)}")
    
    return db_candidat

# ------------------------- OBTENIR TOUS LES CANDIDATS -------------------------
@router.get("/", response_model=List[CandidatBase])
def get_all_candidats(db: Session = Depends(get_db)):
    """Retourne la liste de tous les candidats"""
    return db.query(Candidat).all()

# ------------------------- OBTENIR UN CANDIDAT -------------------------
@router.get("/{numElecteur}", response_model=CandidatBase)
def get_candidat(numElecteur: str, db: Session = Depends(get_db)):
    """Récupère un candidat avec son dernier code de sécurité actif"""
    # Charger les données de l'électeur en une seule requête
    candidat = db.query(Candidat)\
        .options(joinedload(Candidat.electeur))\
        .filter(Candidat.numElecteur == numElecteur)\
        .first()

    if not candidat or not candidat.electeur:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")

    # Récupérer le dernier code actif
    code_actif = code_generator_service.get_active_code(db, numElecteur)
    
    # Construire la réponse avec toutes les données
    return {
        **candidat.__dict__,
        "nom": candidat.electeur.nom,
        "prenom": candidat.electeur.prenom,
        "dateNaissance": candidat.electeur.dateNaissance,
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
        (candidat_update.email is not None and candidat_update.email != candidat.email) or
        (candidat_update.telephone is not None and candidat_update.telephone != candidat.telephone)
    )
    
    # Mise à jour des informations
    for key, value in candidat_update.model_dump(exclude_unset=True).items():
        setattr(candidat, key, value)
    
    candidat.dateDerniereModification = datetime.utcnow()
    db.commit()
    db.refresh(candidat)
    
    # Si les informations de contact sont modifiées, générer un nouveau code et l'envoyer
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
def regenerate_password(numElecteur: str, db: Session = Depends(get_db), send_notifications: bool = True):
    """
    Génère un nouveau mot de passe sécurisé pour un candidat et l'envoie par SMS et email.
    """
    # Vérifier que le candidat existe
    candidat = db.query(Candidat).filter(Candidat.numElecteur == numElecteur).first()
    if not candidat:
        raise HTTPException(status_code=404, detail="Candidat non trouvé.")
    
    # Générer un nouveau code via le service et l'envoyer
    try:
        new_code_entry = code_generator_service.create_security_code(db, numElecteur, send_notifications)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération ou de l'envoi du code: {str(e)}"
        )
    
    # Mettre à jour la date de dernière modification
    candidat.dateDerniereModification = datetime.utcnow()
    db.commit()
    
    return new_code_entry
