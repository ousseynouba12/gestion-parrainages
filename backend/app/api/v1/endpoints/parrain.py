# app/api/v1/endpoints/parrain.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List
from datetime import date

from app.core.database import get_db
from app.models.parrain import Parrain
from app.models.electeur import Electeur
from app.models.candidat import Candidat
from app.schemas.parrain import ParrainBase, ParrainCreate, Parrain as ParrainSchema
from app.services.parrain_code_generator import parrain_code_generator_service
from app.services.hashing import hash_code, verify_code

router = APIRouter()

@router.post("/register", response_model=ParrainSchema, status_code=status.HTTP_201_CREATED)
def register_parrain(parrain_data: ParrainCreate, db: Session = Depends(get_db)):
    """
    Enregistre un nouvel électeur en tant que parrain.
    """
    try:
        # Vérifier l'existence de l'électeur
        electeur = db.query(Electeur).filter(Electeur.numElecteur == parrain_data.numElecteur).first()
        if not electeur:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Électeur {parrain_data.numElecteur} introuvable"
            )

        # Vérifier si déjà parrain
        existing_parrain = db.query(Parrain).filter(Parrain.numElecteur == parrain_data.numElecteur).first()
        if existing_parrain:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cet électeur est déjà un parrain"
            )

        # Vérifier si candidat
        existing_candidat = db.query(Candidat).filter(Candidat.numElecteur == parrain_data.numElecteur).first()
        if existing_candidat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet électeur est déjà un candidat"
            )

        # Générer un code d'authentification
        code = parrain_code_generator_service.generate_code()

        # Hasher le code
        hashed_code = hash_code(code)

        # Créer le parrain avec le code haché
        new_parrain = Parrain(
            numElecteur=parrain_data.numElecteur,
            email=parrain_data.email,
            telephone=parrain_data.telephone,
            codeAuthentification=hashed_code  # Stocker le hash du code
        )

        db.add(new_parrain)
        db.commit()
        db.refresh(new_parrain)

        # Envoyer le code en clair par email
        try:
            parrain_code_generator_service.send_code_email(new_parrain, code)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'envoi du code: {str(e)}"
            )

        # Retourner les informations combinées (Parrain + Electeur)
        response_data = {
            **new_parrain.__dict__,
            "nom": electeur.nom,
            "prenom": electeur.prenom,
            "dateNaissance": electeur.dateNaissance,
            "lieuNaissance": electeur.lieuNaissance,
            "sexe": electeur.sexe,
            "bureauVote": electeur.bureauVote,
        }

        return response_data

    except IntegrityError as e:
        db.rollback()
        if "Duplicate entry" in str(e):
            field = "email" if "email" in str(e) else "telephone"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{field.capitalize()} déjà utilisé"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur intégrité: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )

@router.post("/request-code", status_code=status.HTTP_200_OK)
def request_authentication_code(num_electeur: str, db: Session = Depends(get_db)):
    """
    Demande un nouveau code d'authentification
    """
    try:
        parrain = db.query(Parrain).filter(Parrain.numElecteur == num_electeur).first()
        if not parrain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parrain non trouvé"
            )
        # Générer un nouveau code
        new_code = parrain_code_generator_service.generate_code()

        # Hasher le nouveau code
        hashed_code = hash_code(new_code)

        # Mettre à jour le code dans la base de données
        parrain.codeAuthentification = hashed_code
        db.commit()

        # Envoyer le nouveau code en clair par email
        parrain_code_generator_service.send_code_email(parrain, new_code)

        return {"message": "Nouveau code envoyé"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.post("/verify-code", status_code=status.HTTP_200_OK)
def verify_authentication_code(num_electeur: str, code: str, db: Session = Depends(get_db)):
    """
    Vérifie un code d'authentification
    """
    try:
        parrain = db.query(Parrain).filter(Parrain.numElecteur == num_electeur).first()
        if not parrain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parrain non trouvé"
            )

        # Vérifier si le code correspond au hash stocké
        is_valid = verify_code(code, parrain.codeAuthentification)
        return {"valid": is_valid}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur vérification: {str(e)}"
        )

@router.get("/{num_electeur}", response_model=ParrainSchema)
def get_parrain(num_electeur: str, db: Session = Depends(get_db)):
    """
    Récupère un parrain par son numéro
    """
    parrain = db.query(Parrain).filter(Parrain.numElecteur == num_electeur).first()
    if not parrain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parrain non trouvé"
        )

    # Récupérer les informations de l'électeur
    electeur = db.query(Electeur).filter(Electeur.numElecteur == num_electeur).first()
    if not electeur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Électeur non trouvé"
        )

    # Retourner les informations combinées (Parrain + Electeur)
    response_data = {
        **parrain.__dict__,
        "nom": electeur.nom,
        "prenom": electeur.prenom,
        "dateNaissance": electeur.dateNaissance,
        "lieuNaissance": electeur.lieuNaissance,
        "sexe": electeur.sexe,
        "bureauVote": electeur.bureauVote,
    }

    return response_data

@router.get("/", response_model=List[ParrainSchema])
def get_all_parrains(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Liste tous les parrains
    """
    parrains = db.query(Parrain).offset(skip).limit(limit).all()

    # Joindre les informations de l'électeur pour chaque parrain
    response_data = []
    for parrain in parrains:
        electeur = db.query(Electeur).filter(Electeur.numElecteur == parrain.numElecteur).first()
        if electeur:
            response_data.append({
                **parrain.__dict__,
                "nom": electeur.nom,
                "prenom": electeur.prenom,
                "dateNaissance": electeur.dateNaissance,
                "lieuNaissance": electeur.lieuNaissance,
                "sexe": electeur.sexe,
                "bureauVote": electeur.bureauVote,
            })

    return response_data

@router.delete("/{num_electeur}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parrain(num_electeur: str, db: Session = Depends(get_db)):
    """
    Supprime un parrain
    """
    parrain = db.query(Parrain).filter(Parrain.numElecteur == num_electeur).first()
    if not parrain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parrain non trouvé"
        )

    try:
        db.delete(parrain)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur suppression: {str(e)}"
        )