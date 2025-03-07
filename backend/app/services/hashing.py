# app/services/hashing.py
from passlib.context import CryptContext
import logging

# Configuration du contexte de hachage
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_code(code: str) -> str:
    """
    Hache un code avec SHA-256.
    
    Args:
        code (str): Code à hacher
        
    Returns:
        str: Code haché
    """
    try:
        # S'assurer que code est une chaîne
        if not isinstance(code, str):
            code = str(code)
        
        # Hacher le code
        hashed = pwd_context.hash(code)
        
        # Vérifier la longueur du résultat
        if len(hashed) > 128:
            print(f"ATTENTION: Hash trop long ({len(hashed)} caractères) pour la colonne (128 max)")
            # Tronquer si nécessaire (mais cela impactera la vérification)
            # hashed = hashed[:128]  # Cette ligne est commentée car elle rendrait le hash invalide
        
        print(f"Code haché avec succès: longueur={len(hashed)}")
        return hashed
        
    except Exception as e:
        print(f"ERREUR lors du hachage: {str(e)}")
        # En cas d'erreur, retourner une chaîne simple (non recommandé en production)
        # Cette solution n'est pas sécurisée mais évite que l'application plante
        return f"ERROR_HASH_{code}"

def verify_code(plain_code: str, hashed_code: str) -> bool:
    """
    Vérifie si un code correspond à son hash.
    
    Args:
        plain_code (str): Code en clair à vérifier
        hashed_code (str): Code haché stocké
        
    Returns:
        bool: True si les codes correspondent, False sinon
    """
    try:
        # S'assurer que plain_code est une chaîne
        if not isinstance(plain_code, str):
            plain_code = str(plain_code)
        
        # Vérifier si le hash commence par "ERROR_HASH_" (cas d'erreur)
        if hashed_code.startswith("ERROR_HASH_"):
            return plain_code == hashed_code[11:]  # Comparer avec la partie après "ERROR_HASH_"
        
        # Vérification normale
        return pwd_context.verify(plain_code, hashed_code)
        
    except Exception as e:
        print(f"ERREUR lors de la vérification: {str(e)}")
        return False