from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from app.core.database import get_db
from app.models.periode_parrainage import PeriodeParrainage as PeriodeParrainageModel
from app.schemas.periode_parrainage import PeriodeParrainageBase, PeriodeParrainage as PeriodeParrainageSchema

router = APIRouter()

def validate_dates(date_debut: date, date_fin: date):
    """Valide les contraintes de dates pour une période de parrainage"""
    today = date.today()
    six_months_later = today + timedelta(days=180)  # 6 mois = environ 180 jours
    
    if date_debut >= date_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de début doit être antérieure à la date de fin"
        )
    
    if date_debut < six_months_later:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de début doit être au moins 6 mois après la date actuelle"
        )
    
    return True

# @router.get("/check-status", response_model=dict)
# def check_system_status(db: Session = Depends(get_db)):
#     """
#     Vérifier l'état du système de parrainage
#     - Retourne si les enregistrements et parrainages sont actuellement autorisés
#     """
#     today = date.today()
    
#     # Rechercher une période active
#     active_periode = db.query(PeriodeParrainageModel).filter(
#         PeriodeParrainageModel.dateDebut <= today,
#         PeriodeParrainageModel.dateFin >= today,
#         PeriodeParrainageModel.etat == "OUVERT"
#     ).first()
    
#     # Déterminer les permissions
#     is_registration_allowed = False
#     is_parrainages_allowed = False
#     is_candidate_addition_allowed = True
    
#     if active_periode:
#         is_registration_allowed = True
#         is_parrainages_allowed = True
#         is_candidate_addition_allowed = False
    
#     return {
#         "registrations_allowed": is_registration_allowed,
#         "parrainages_allowed": is_parrainages_allowed,
#         "candidate_addition_allowed": is_candidate_addition_allowed,
#         "active_periode_id": active_periode.idPeriode if active_periode else None
#     }

@router.post("/", response_model=PeriodeParrainageSchema, status_code=status.HTTP_201_CREATED)
def create_periode(periode: PeriodeParrainageBase, db: Session = Depends(get_db)):
    """
    Créer une nouvelle période de parrainage
    - Valide qu'aucune période n'existe déjà
    - Valide les contraintes de dates
    """
    # Vérifier s'il existe déjà une période
    existing_period = db.query(PeriodeParrainageModel).first()
    if existing_period:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une période de parrainage est déjà enregistrée"
        )

    # Valider les dates
    validate_dates(periode.dateDebut, periode.dateFin)
    
    # Créer la période avec l'état FERME par défaut
    db_periode = PeriodeParrainageModel(
        dateDebut=periode.dateDebut,
        dateFin=periode.dateFin,
        etat="FERME"
    )
    
    db.add(db_periode)
    db.commit()
    db.refresh(db_periode)
    return db_periode

@router.get("/active", response_model=PeriodeParrainageSchema)
def get_active_periode(db: Session = Depends(get_db)):
    """
    Récupérer la période de parrainage active (si elle existe)
    - Une période est active si la date actuelle est entre la date de début et la date de fin
    """
    today = date.today()
    active_periode = db.query(PeriodeParrainageModel).filter(
        PeriodeParrainageModel.dateDebut <= today,
        PeriodeParrainageModel.dateFin >= today
    ).first()
    
    if active_periode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune période de parrainage active en ce moment"
        )
    
    return active_periode


@router.get("/", response_model=List[PeriodeParrainageSchema])
def read_periodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer toutes les périodes de parrainage"""
    periodes = db.query(PeriodeParrainageModel).offset(skip).limit(limit).all()
    return periodes

# @router.get("/{periode_id}", response_model=PeriodeParrainageSchema)
# def read_periode(periode_id: int, db: Session = Depends(get_db)):
#     """Récupérer une période de parrainage spécifique par son ID"""
#     db_periode = db.query(PeriodeParrainageModel).filter(PeriodeParrainageModel.idPeriode == periode_id).first()
#     if db_periode is None:
#         raise HTTPException(status_code=404, detail="Période de parrainage non trouvée")
#     return db_periode

@router.put("/{periode_id}", response_model=PeriodeParrainageSchema)
def update_periode(periode_id: int, periode: PeriodeParrainageBase, db: Session = Depends(get_db)):
    """
    Mettre à jour une période de parrainage existante
    - Valide que la date de début est inférieure à la date de fin
    - Valide que la date de début est au moins 6 mois après la date actuelle
    """
    db_periode = db.query(PeriodeParrainageModel).filter(PeriodeParrainageModel.idPeriode == periode_id).first()
    if db_periode is None:
        raise HTTPException(status_code=404, detail="Période de parrainage non trouvée")
    
    # Valider les dates
    validate_dates(periode.dateDebut, periode.dateFin)
    
    # Mettre à jour les champs
    db_periode.dateDebut = periode.dateDebut
    db_periode.dateFin = periode.dateFin
    # Ne pas changer l'état ici, il est géré par les routes spécifiques
    
    db.commit()
    db.refresh(db_periode)
    return db_periode

@router.delete("/{periode_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_periode(periode_id: int, db: Session = Depends(get_db)):
    """Supprimer une période de parrainage"""
    db_periode = db.query(PeriodeParrainageModel).filter(PeriodeParrainageModel.idPeriode == periode_id).first()
    if db_periode is None:
        raise HTTPException(status_code=404, detail="Période de parrainage non trouvée")
    
    db.delete(db_periode)
    db.commit()
    return None


@router.post("/update-status", status_code=status.HTTP_200_OK)
def update_system_status(db: Session = Depends(get_db)):
    """
    Mettre à jour automatiquement l'état des périodes de parrainage
    - Ouvre automatiquement les périodes dont la date de début est atteinte
    - Ferme automatiquement les périodes dont la date de fin est dépassée
    - Cette route peut être appelée via un job cron quotidien
    """
    today = date.today()
    
    # Ouvrir les périodes dont la date de début est atteinte
    periodes_to_open = db.query(PeriodeParrainageModel).filter(
        PeriodeParrainageModel.dateDebut <= today,
        PeriodeParrainageModel.dateFin >= today,
        PeriodeParrainageModel.etat == "FERME"
    ).all()
    
    for periode in periodes_to_open:
        periode.etat = "OUVERT"
    
    # Fermer les périodes dont la date de fin est dépassée
    periodes_to_close = db.query(PeriodeParrainageModel).filter(
        PeriodeParrainageModel.dateFin < today,
        PeriodeParrainageModel.etat == "OUVERT"
    ).all()
    
    for periode in periodes_to_close:
        periode.etat = "FERME"
    
    db.commit()
    
    return {
        "periodes_opened": len(periodes_to_open),
        "periodes_closed": len(periodes_to_close)
    }