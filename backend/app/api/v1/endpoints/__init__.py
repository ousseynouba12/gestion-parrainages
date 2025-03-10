from app.api.v1.endpoints import electoral
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    membre_dge,
    electeur,
    candidat,
    parrain,
    parrainage,
    periode_parrainage,
    code_authentification_parrain,
    electeur_temporaire_valide,
    electoral
    #audit
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
router.include_router(membre_dge.router, prefix="/membres", tags=["Membres DGE"])
router.include_router(electeur.router, prefix="/electeurs", tags=["Électeurs"])
router.include_router(candidat.router, prefix="/candidats", tags=["Candidats"])
router.include_router(parrain.router, prefix="/parrain", tags=["Parrain"])
router.include_router(parrainage.router, prefix="/parrainages", tags=["Parrainages"])
router.include_router(periode_parrainage.router, prefix="/periodes", tags=["Périodes de Parrainage"])
router.include_router(electoral.router, prefix="/electoral", tags=["Gestion du fichier électoral"])

#router.include_router(tentative_upload.router, prefix="/tentatives", tags=["Tentatives d’Upload"])
#router.include_router(code_securite_candidat.router, prefix="/codes_candidats", tags=["Codes Sécurité Candidats"])
router.include_router(code_authentification_parrain.router, prefix="/codes_parrains", tags=["Codes Authentification Parrains"])
router.include_router(electeur_temporaire_valide.router, prefix="/electeurs_temp_valides", tags=["Électeurs Temporaires Validés"])
#router.include_router(audit.router, prefix="/audit", tags=["Logs d'Audit"])

