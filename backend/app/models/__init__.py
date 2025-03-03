# app/models/__init__.py

# Tables de base (sans dépendances externes)
from app.models.membre_dge import MembreDGE
from app.models.electeur import Electeur
from app.models.periode_parrainage import PeriodeParrainage

# Tables avec dépendances simples
from app.models.fichier_electoral import FichierElectoral  # dépend de membre_dge
from app.models.tentative_upload import TentativeUpload    # dépend de fichier_electoral
from app.models.candidat import Candidat                   # dépend probablement de electeur
from app.models.parrain import Parrain                     # dépend probablement de electeur

# Tables avec dépendances multiples
from app.models.electeur_temporaire import ElecteurTemporaire              # dépend de tentative_upload
from app.models.electeur_temporaire_valide import ElecteurTemporaireValide # dépend de electeur_temporaire
from app.models.parrainage import Parrainage                               # dépend de parrain et candidat
from app.models.code_securite_candidat import CodeSecuriteCandidat         # dépend de candidat
from app.models.code_authentification_parrain import CodeAuthentificationParrain # dépend de parrain

# Logs (peuvent dépendre de tout)
from app.models.audit_log import AuditLog
