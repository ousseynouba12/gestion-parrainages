# app/services/parrain_code_generator.py
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.code_authentification_parrain import CodeAuthentificationParrain
from app.models.parrain import Parrain
from app.services.notification_service import NotificationService

class ParrainCodeGeneratorService:
    def __init__(self):
        self.notification_service = NotificationService()

    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Génère un code aléatoire de longueur spécifiée (par défaut 6 caractères)"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def create_authentication_code(self, db: Session, num_parrain: str, send_notifications: bool = True) -> CodeAuthentificationParrain:
        """
        Crée un nouveau code d'authentification pour un parrain.
        Génère un nouveau code et l'envoie par email si demandé.
        
        Args:
            db (Session): Session de base de données
            num_parrain (str): Numéro d'électeur du parrain
            send_notifications (bool): Si True, envoie le code par email
            
        Returns:
            CodeAuthentificationParrain: Nouvelle entrée de code d'authentification
        """
        # Récupérer les informations du parrain
        parrain = db.query(Parrain).filter(Parrain.numElecteur == num_parrain).first()
        if not parrain:
            raise ValueError(f"Parrain avec ID {num_parrain} non trouvé")
        
        parrain.tentatives_validation = 0
        parrain.derniere_tentative = None

        # Générer et enregistrer un nouveau code
        new_code = self.generate_code()
        new_code_entry = CodeAuthentificationParrain(
            numParrain=num_parrain,
            code=new_code,
            dateEnvoi=datetime.utcnow()
        )
        db.add(new_code_entry)
        db.commit()
        db.refresh(new_code_entry)

        # Envoyer le code par email si demandé
        if send_notifications:
            self.send_code_email(parrain, new_code)

        return new_code_entry

    def send_code_email(self, parrain: Parrain, code: str) -> bool:
        """
        Envoie le code d'authentification par email au parrain.
        
        Args:
            parrain (Parrain): Objet parrain contenant email
            code (str): Code d'authentification à envoyer
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        now = datetime.utcnow()

        from app.models.electeur import Electeur
        from sqlalchemy.orm import Session
        from app.core.database import SessionLocal

        db = SessionLocal()
        electeur = db.query(Electeur).filter(Electeur.numElecteur == parrain.numElecteur).first()

        # Préparation du contexte pour les templates
        template_context = {
            "prenom": electeur.prenom if electeur else "Électeur",
            "nom": electeur.nom if electeur else "",
            "code": code,
            "date_envoi": now
        }

        # Envoi par email
        if parrain.email:
            return self.notification_service.send_email(
                to_email=parrain.email,
                subject="Votre code de validation pour le parrainage",
                content="",  # Non utilisé car on utilise un template
                template_name="code_validation",
                template_context=template_context
            )
        return False
    
    @staticmethod
    def verify_code(db: Session, num_parrain: str, code: str, expiration_minutes: int = 2) -> bool:
        """
        Vérifie si le code fourni est valide pour un parrain donné.
        Un code est valide s'il correspond, n'a pas expiré et si le nombre de tentatives n'est pas dépassé.
        
        Args:
            db (Session): Session de base de données
            num_parrain (str): Numéro d'électeur du parrain
            code (str): Code à vérifier
            expiration_minutes (int): Délai d'expiration en minutes
            
        Returns:
            bool: True si le code est valide, False sinon
        """
        MAX_TENTATIVES = 3  # Nombre maximum de tentatives autorisées
        DELAI_BLOCAGE = timedelta(minutes=15)  # Délai de blocage après dépassement des tentatives

        # Récupérer le parrain
        parrain = db.query(Parrain).filter(Parrain.numElecteur == num_parrain).first()
        if not parrain:
            raise ValueError("Parrain non trouvé")
        # Vérifier si le parrain est bloqué
        if (parrain.derniere_tentative and (datetime.utcnow() - parrain.derniere_tentative) < DELAI_BLOCAGE) and parrain.tentatives_validation >= MAX_TENTATIVES:
            raise ValueError("Trop de tentatives. Veuillez réessayer plus tard.")

        # Récupérer le code le plus récent pour ce parrain
        latest_code = db.query(CodeAuthentificationParrain).filter(
            CodeAuthentificationParrain.numParrain == num_parrain
        ).order_by(CodeAuthentificationParrain.dateEnvoi.desc()).first()

        if not latest_code:
            return False

        # Vérifier si le code correspond et n'a pas expiré
        expiration_time = latest_code.dateEnvoi + timedelta(minutes=expiration_minutes)
        now = datetime.utcnow()

        if latest_code.code == code and now <= expiration_time:
            # Réinitialiser les tentatives si le code est valide
            parrain.tentatives_validation = 0
            parrain.derniere_tentative = None
            db.commit()
            return True

        # Si le code est invalide, incrémenter le nombre de tentatives
        parrain.tentatives_validation += 1
        parrain.derniere_tentative = datetime.utcnow()
        db.commit()


        return False
# Créer une instance singleton du service
parrain_code_generator_service = ParrainCodeGeneratorService()