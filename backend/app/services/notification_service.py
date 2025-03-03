# app/services/notification_service.py

import smtplib
import ssl
import os
import requests
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from jinja2 import Environment, FileSystemLoader, select_autoescape

class NotificationSettings(BaseSettings):
    # Paramètres Email (SMTP)
    SMTP_SERVER: str = os.getenv('SMTP_SERVER')
    SMTP_PORT: int = os.getenv('SMTP_PORT')
    SMTP_USER: str = os.getenv('SMTP_USER')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD')
    EMAIL_SENDER: str = os.getenv('EMAIL_SENDER')
    
    # # Paramètres SMS (exemple avec OVH SMS)
    # OVH_SMS_ENDPOINT: str = "https://www.ovh.com/cgi-bin/sms/http2sms.cgi"
    # OVH_SMS_ACCOUNT: str = "votre_compte_sms"
    # OVH_SMS_USER: str = "votre_utilisateur_sms"
    # OVH_SMS_PASSWORD: str = "votre_mot_de_passe_sms"
    # OVH_SMS_FROM: str = "ELECTIONS"
    
    # Dossier contenant les templates
    TEMPLATES_DIR: str = "app/templates"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
class NotificationService:
    def __init__(self):
        self.settings = NotificationSettings()
        
        # Configuration de Jinja2 pour les templates
        self.templates = Environment(
            loader=FileSystemLoader(self.settings.TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def send_email(self, to_email: str, subject: str, content: str, 
                  template_name: Optional[str] = None, template_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Envoie un email au destinataire spécifié.
        
        Args:
            to_email (str): Adresse email du destinataire
            subject (str): Sujet de l'email
            content (str): Contenu de l'email (utilisé si pas de template)
            template_name (str, optional): Nom du template à utiliser
            template_context (Dict[str, Any], optional): Contexte pour le template
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Création du message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.settings.EMAIL_SENDER
            message["To"] = to_email
            
            # Utilisation du template si spécifié
            if template_name and template_context:
                template = self.templates.get_template(f"{template_name}.html")
                html_content = template.render(**template_context)
                message.attach(MIMEText(html_content, "html"))
                
                # Version texte (fallback)
                template_text = self.templates.get_template(f"{template_name}.txt")
                text_content = template_text.render(**template_context)
                message.attach(MIMEText(text_content, "plain"))
            else:
                # Utilisation du contenu direct
                message.attach(MIMEText(content, "plain"))
            
            # Connexion au serveur SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP(self.settings.SMTP_SERVER, self.settings.SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(self.settings.SMTP_USER, self.settings.SMTP_PASSWORD)
                server.sendmail(self.settings.EMAIL_SENDER, to_email, message.as_string())
                
            print(f"Email envoyé à {to_email} avec le sujet: {subject}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False


    # Méthode pour envoyer des SMS via Twilio
    # def send_sms_callmebot(self, phone_number: str, message: str) -> bool:
    #     """
    #     Envoie un message WhatsApp via CallMeBot.
        
    #     Args:
    #         phone_number (str): Numéro de téléphone du destinataire (format international sans "+")
    #         message (str): Contenu du message
            
    #     Returns:
    #         bool: True si l'envoi a réussi, False sinon
    #     """
    #     # api_key = os.getenv("CALLMEBOT_API_KEY")
    #     # phone_number = os.getenv("PHONE_NUMBER")

    #     # print(f"CALLMEBOT_API_KEY: {api_key}")
    #     # print(f"PHONE_NUMBER: {phone_number}")

    #     try:
    #         # Récupération de l'API Key CallMeBot depuis les variables d'environnement
    #         api_key = os.environ.get("CALLMEBOT_API_KEY")
    #         phone_number = os.getenv("PHONE_NUMBER")

    #         if not api_key:
    #             raise ValueError("API Key CallMeBot manquante. Définissez CALLMEBOT_API_KEY dans .env.")

    #         # Formatage du numéro et du message
    #         clean_number = ''.join(filter(str.isdigit, phone_number))  # Supprime tout sauf les chiffres
    #         encoded_message = urllib.parse.quote_plus(message)  # Encode le message pour l'URL
            
    #         # URL de l'API CallMeBot
    #         url = f"https://api.callmebot.com/whatsapp.php?phone={clean_number}&text={encoded_message}&apikey={api_key}"
            
    #         # Envoi de la requête
    #         response = requests.get(url)
            
    #         if response.status_code == 200:
    #             print(f"Message WhatsApp envoyé à {phone_number} ✅")
    #             return True
    #         else:
    #             print(f"Erreur lors de l'envoi : {response.status_code} - {response.text}")
    #             return False
            
    #     except Exception as e:
    #         print(f"Erreur lors de l'envoi du message WhatsApp via CallMeBot: {str(e)}")
    #         return False    
    
    # def send_sms(self, phone_number: str, message: str) -> bool:
    #     """
    #     Envoie un SMS au numéro spécifié (implémentation OVH SMS).
        
    #     Args:
    #         phone_number (str): Numéro de téléphone du destinataire (format international)
    #         message (str): Contenu du SMS
            
    #     Returns:
    #         bool: True si l'envoi a réussi, False sinon
    #     """
    #     try:
    #         # Formatage du numéro (suppression des espaces et autres caractères)
    #         clean_number = ''.join(filter(str.isdigit, phone_number))
            
    #         # S'assurer que le numéro est au format international
    #         if not clean_number.startswith('00') and not clean_number.startswith('+'):
    #             # Ajouter l'indicatif français par défaut si nécessaire
    #             clean_number = '0033' + clean_number[1:] if clean_number.startswith('0') else '0033' + clean_number
            
    #         # Préparation des données pour l'API OVH SMS
    #         params = {
    #             'account': self.settings.OVH_SMS_ACCOUNT,
    #             'login': self.settings.OVH_SMS_USER,
    #             'password': self.settings.OVH_SMS_PASSWORD,
    #             'from': self.settings.OVH_SMS_FROM,
    #             'to': clean_number,
    #             'message': message,
    #             'noStop': 1  # Pour désactiver le STOP pour les SMS transactionnels
    #         }
            
    #         # Envoi du SMS via l'API OVH
    #         response = requests.get(self.settings.OVH_SMS_ENDPOINT, params=params)
            
    #         # Vérification de la réponse
    #         if response.status_code == 200 and 'OK' in response.text:
    #             print(f"SMS envoyé à {phone_number}")
    #             return True
    #         else:
    #             print(f"Erreur lors de l'envoi du SMS: {response.text}")
    #             return False
                
    #     except Exception as e:
    #         print(f"Erreur lors de l'envoi du SMS: {str(e)}")
    #         return False



