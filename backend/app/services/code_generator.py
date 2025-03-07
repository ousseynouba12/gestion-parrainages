# app/services/code_generator.py
import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.code_securite_candidat import CodeSecuriteCandidat
from app.models.candidat import Candidat
from app.services.notification_service import NotificationService
from app.services.hashing import hash_code, verify_code  # Importer les fonctions de hachage

class CodeGeneratorService:
    def __init__(self):
        self.notification_service = NotificationService()

    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Génère un code aléatoire de longueur spécifiée (par défaut 6 caractères)"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def create_security_code(self, db: Session, num_candidat: str, send_notifications: bool = True) -> CodeSecuriteCandidat:
        """
        Crée un nouveau code de sécurité pour un candidat.
        Désactive les anciens codes, génère un nouveau, le hache et l'envoie par SMS et email si demandé.
        Args:
            db (Session): Session de base de données
            num_candidat (str): Numéro d'électeur du candidat
            send_notifications (bool): Si True, envoie le code par SMS et email
        Returns:
            CodeSecuriteCandidat: Nouvelle entrée de code de sécurité
        """
        # Récupérer les informations du candidat
        candidat = db.query(Candidat).filter(Candidat.numElecteur == num_candidat).first()
        if not candidat:
            raise ValueError(f"Candidat avec ID {num_candidat} non trouvé")

        # Vérification des codes existants pour diagnostiquer
        existing_codes = db.query(CodeSecuriteCandidat).filter(
            CodeSecuriteCandidat.numCandidat == num_candidat
        ).all()
        print(f"Codes existants pour candidat {num_candidat}: {len(existing_codes)}")

        # Désactiver les anciens codes
        db.query(CodeSecuriteCandidat).filter(
            CodeSecuriteCandidat.numCandidat == num_candidat,
            CodeSecuriteCandidat.estActif == True
        ).update({"estActif": False})
        
        # Commit pour s'assurer que les désactivations sont enregistrées
        db.commit()

        # Générer un nouveau code
        new_code = self.generate_code()
        
        # Hasher le code avant de le stocker
        hashed_code = hash_code(new_code)
        print(f"Code généré: {new_code} (longueur hachée: {len(hashed_code)})")

        # Enregistrer le nouveau code haché
        try:
            new_code_entry = CodeSecuriteCandidat(
                numCandidat=num_candidat,
                code=hashed_code,  # Stocker le code haché
                dateEnvoi=datetime.utcnow(),
                estActif=True  # Activer le nouveau code
            )
            
            db.add(new_code_entry)
            db.flush()  # Flush pour obtenir l'ID sans committer
            print(f"Nouveau code créé avec ID temporaire: {new_code_entry.idCode}")
            
            db.commit()
            db.refresh(new_code_entry)
            print(f"Code sécurité enregistré avec succès: ID={new_code_entry.idCode}")
        except Exception as e:
            db.rollback()
            print(f"ERREUR lors de l'enregistrement du code: {str(e)}")
            raise

        # Envoyer le code en clair par SMS et email si demandé
        if send_notifications:
            try:
                self.send_code_notifications(candidat, new_code)
            except Exception as e:
                print(f"Erreur lors de l'envoi des notifications: {str(e)}")
                # Ne pas faire échouer la fonction si l'envoi échoue

        return new_code_entry

    def send_code_notifications(self, candidat: Candidat, code: str) -> dict:
        """
        Envoie le code de sécurité par SMS et email au candidat.
        Args:
            candidat (Candidat): Objet candidat contenant email et téléphone
            code (str): Code de sécurité à envoyer
        Returns:
            dict: Statut des envois (email_sent, sms_sent)
        """
        result = {"email_sent": False, "sms_sent": False}
        now = datetime.utcnow()
        
        from app.models.electeur import Electeur
        from sqlalchemy.orm import Session
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        electeur = db.query(Electeur).filter(Electeur.numElecteur == candidat.numElecteur).first()
        
        # Préparation du contexte pour les templates
        template_context = {
            "prenom": electeur.prenom if electeur else "Candidat",
            "nom": electeur.nom if electeur else "",
            "code": code,
            "date_envoi": now
        }
        
        # Préparation du contenu SMS (plus court)
        sms_content = f"[ELECTIONS] Votre code de sécurité: {code}. Valable pour votre espace candidat."
        
        # Envoi par email si disponible
        if candidat.email:
            try:
                result["email_sent"] = self.notification_service.send_email(
                    to_email=candidat.email,
                    subject="Votre code de sécurité pour l'élection",
                    content="",  # Non utilisé car on utilise un template
                    template_name="code_securite",
                    template_context=template_context
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        
        # Envoi par SMS si disponible
        # if candidat.telephone:
        #     try:
        #         result["sms_sent"] = self.notification_service.send_sms_callmebot(
        #             phone_number=candidat.telephone,
        #             message=sms_content
        #         )
        #     except Exception as e:
        #         print(f"Erreur lors de l'envoi du SMS: {str(e)}")
        
        return result

    @staticmethod
    def get_active_code(db: Session, num_candidat: str) -> CodeSecuriteCandidat:
        """Récupère le code de sécurité actif le plus récent pour un candidat"""
        return db.query(CodeSecuriteCandidat).filter(
            CodeSecuriteCandidat.numCandidat == num_candidat,
            CodeSecuriteCandidat.estActif == True
        ).order_by(CodeSecuriteCandidat.dateEnvoi.desc()).first()

# Créer une instance singleton du service
code_generator_service = CodeGeneratorService()