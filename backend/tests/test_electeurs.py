import requests
import hashlib
import os
import json
import time
from pprint import pprint

# Configuration
BASE_URL = "http://localhost:8000/api/v1"  # Ajustez si nécessaire
USERNAME = "ousseynou@esp.sn"
PASSWORD = "passer"

# Chemins des fichiers de test
FICHIER_UTF8_AVEC_INVALIDES = "/Users/ousseynouba/gestion-parrainages/backend/csv_file/electeurs_utf8_avec_invalides.csv"
FICHIER_LATIN1 = "/Users/ousseynouba/gestion-parrainages/backend/csv_file/electeurs_latin1.csv"

# Variables globales pour stocker les données entre les requêtes
token = None
tentative_id = None

def calculer_checksum(fichier_path):
    """Calcule le checksum SHA256 d'un fichier"""
    sha256_hash = hashlib.sha256()
    with open(fichier_path, "rb") as f:
        # Lire le fichier par blocs pour les fichiers volumineux
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def obtenir_token():
    """Obtient un token d'authentification"""
    global token
    
    print("\n=== 1. Obtention du token d'authentification ===")
    
    url = f"{BASE_URL}/auth/token"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        token = token_data["access_token"]
        
        print(f"✅ Token obtenu avec succès: {token[:20]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'obtention du token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def verifier_profil():
    """Vérifie les informations du profil utilisateur"""
    global token
    
    print("\n=== 2. Vérification du profil utilisateur ===")
    
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        profile = response.json()
        print(f"✅ Profil récupéré avec succès:")
        print(f"   ID: {profile['id']}")
        print(f"   Email: {profile['email']}")
        print(f"   Rôle: {profile['role']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération du profil: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def verifier_statut_upload():
    """Vérifie si un upload est autorisé"""
    global token
    
    print("\n=== 3. Vérification du statut d'upload ===")
    
    url = f"{BASE_URL}/electoral/statut-upload"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        statut = response.json()
        print(f"✅ Statut d'upload récupéré: {statut['upload_autorise']}")
        
        if not statut['upload_autorise']:
            print("⚠️ Un reset de l'état d'upload est nécessaire avant de continuer.")
            reinitialiser_etat_upload()
        
        return statut['upload_autorise']
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la vérification du statut d'upload: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def reinitialiser_etat_upload():
    """Réinitialise l'état d'upload (admin uniquement)"""
    global token
    
    print("\n=== 4. Réinitialisation de l'état d'upload ===")
    
    url = f"{BASE_URL}/electoral/reinitialiser-etat-upload"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        resultat = response.json()
        print(f"✅ Réinitialisation effectuée: {resultat['message']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def uploader_fichier_electoral(fichier_path):
    """Upload un fichier électoral"""
    global token, tentative_id
    
    print(f"\n=== 5. Upload du fichier électoral ({os.path.basename(fichier_path)}) ===")
    
    # Calculer le checksum du fichier
    checksum = calculer_checksum(fichier_path)
    print(f"Checksum calculé: {checksum}")
    
    url = f"{BASE_URL}/electoral/upload-fichier-electoral"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Préparer les données multipart/form-data
    files = {
        'file': (os.path.basename(fichier_path), open(fichier_path, 'rb'), 'text/csv')
    }
    data = {
        'checksum': checksum
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        
        resultat = response.json()
        print(f"✅ Upload réussi: {resultat['message']}")
        
        if 'tentative_id' in resultat:
            tentative_id = resultat['tentative_id']
            print(f"ID de tentative: {tentative_id}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'upload: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def controler_electeurs():
    """Contrôle les données des électeurs"""
    global token, tentative_id
    
    if tentative_id is None:
        print("❌ Aucun ID de tentative disponible. L'upload a peut-être échoué.")
        return False
    
    print(f"\n=== 6. Contrôle des électeurs (tentative {tentative_id}) ===")
    
    url = f"{BASE_URL}/electoral/controler-electeurs/{tentative_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        resultat = response.json()
        print(f"✅ Contrôle terminé: {resultat['message']}")
        print("Statistiques:")
        pprint(resultat['statistiques'])
        print(f"Peut valider: {resultat['peut_valider']}")
        
        return resultat['peut_valider']
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du contrôle des électeurs: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def obtenir_statistiques():
    """Récupère les statistiques d'importation"""
    global token, tentative_id
    
    if tentative_id is None:
        print("❌ Aucun ID de tentative disponible.")
        return False
    
    print(f"\n=== 7. Obtention des statistiques d'importation (tentative {tentative_id}) ===")
    
    url = f"{BASE_URL}/electoral/statistiques-importation/{tentative_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        stats = response.json()
        print("✅ Statistiques récupérées:")
        pprint(stats)
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def obtenir_electeurs_problematiques():
    """Récupère la liste des électeurs problématiques"""
    global token, tentative_id
    
    if tentative_id is None:
        print("❌ Aucun ID de tentative disponible.")
        return False
    
    print(f"\n=== 8. Obtention des électeurs problématiques (tentative {tentative_id}) ===")
    
    url = f"{BASE_URL}/electoral/electeurs-problematiques/{tentative_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        electeurs = response.json()
        print(f"✅ Électeurs problématiques récupérés: {electeurs['count']}")
        if electeurs['count'] > 0:
            print("Exemples d'erreurs:")
            for i, electeur in enumerate(electeurs['electeurs'][:3]):
                print(f"  {i+1}. {electeur['numElecteur']} ({electeur['nom']} {electeur['prenom']}): {electeur['erreur']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des électeurs problématiques: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def valider_importation():
    """Valide l'importation des électeurs"""
    global token, tentative_id
    
    if tentative_id is None:
        print("❌ Aucun ID de tentative disponible.")
        return False
    
    print(f"\n=== 9. Validation de l'importation (tentative {tentative_id}) ===")
    
    url = f"{BASE_URL}/electoral/valider-importation/{tentative_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        resultat = response.json()
        print(f"✅ Validation réussie: {resultat['message']}")
        print(f"Nombre d'électeurs importés: {resultat['nb_electeurs_importes']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la validation: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def deconnexion():
    """Déconnexion (côté client)"""
    global token
    
    print("\n=== 10. Déconnexion ===")
    
    url = f"{BASE_URL}/auth/logout"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        resultat = response.json()
        print(f"✅ Déconnexion: {resultat['message']}")
        token = None
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la déconnexion: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Détails: {e.response.text}")
        return False

def executer_test_complet():
    """Exécute le test complet du flux"""
    print("=== DÉMARRAGE DU TEST COMPLET ===")
    print(f"URL de base: {BASE_URL}")
    print(f"Utilisateur: {USERNAME}")
    print()
    
    # 1. Authentification
    if not obtenir_token():
        print("❌ Échec de l'authentification. Arrêt des tests.")
        return
    
    # 2. Vérification du profil
    if not verifier_profil():
        print("❌ Échec de la vérification du profil. Arrêt des tests.")
        return
    
    # 3. Vérification du statut d'upload
    if not verifier_statut_upload():
        print("⚠️ Upload non autorisé. Tentative de réinitialisation...")
        if not reinitialiser_etat_upload():
            print("❌ Échec de la réinitialisation. Arrêt des tests.")
            return
    
    # 4. Upload du fichier électoral (UTF-8 avec des électeurs invalides)
    print("\nTest avec fichier UTF-8 contenant des électeurs invalides:")
    if not uploader_fichier_electoral(FICHIER_UTF8_AVEC_INVALIDES):
        print("❌ Échec de l'upload du fichier. Tentative avec le deuxième fichier...")
        # Réessayer avec le fichier latin1
        if not uploader_fichier_electoral(FICHIER_LATIN1):
            print("❌ Échec de l'upload des deux fichiers. Arrêt des tests.")
            return
    
    # 5. Contrôle des électeurs
    if not controler_electeurs():
        print("⚠️ Des problèmes ont été détectés dans les données des électeurs.")
    
    # 6. Obtention des statistiques
    obtenir_statistiques()
    
    # 7. Obtention des électeurs problématiques
    obtenir_electeurs_problematiques()
    
    # 8. Validation de l'importation (si possible)
    try:
        valider_importation()
    except Exception as e:
        print(f"⚠️ Validation non effectuée: {e}")
    
    # 9. Déconnexion
    deconnexion()
    
    print("\n=== TEST COMPLET TERMINÉ ===")

if __name__ == "__main__":
    executer_test_complet()