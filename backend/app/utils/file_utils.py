# app/utils/file_utils.py
import hashlib
import csv
import io
import os
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
import codecs

def calculate_sha256(file_content: bytes) -> str:
    """Calcule l'empreinte SHA256 d'un contenu de fichier"""
    return hashlib.sha256(file_content).hexdigest()

def is_utf8(content: bytes) -> bool:
    """Vérifie si le contenu est encodé en UTF-8"""
    try:
        content.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

def save_uploaded_file(file_content: bytes, filename: str, directory: str) -> str:
    """
    Sauvegarde un fichier téléchargé dans le répertoire spécifié
    Retourne le chemin complet du fichier
    """
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(directory, f"{timestamp}_{filename}")
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path

def parse_csv_electeurs(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parse un fichier CSV d'électeurs et retourne:
    - Les lignes valides (format correct)
    - Les lignes invalides (format incorrect)
    
    Cette fonction ne vérifie que la structure et le format basique,
    pas la validité des données (ce qui sera fait par ControlerElecteurs)
    """
    valid_rows = []
    invalid_rows = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                line_number = i
                required_fields = ['numElecteur', 'numCIN', 'nom', 'prenom', 
                                  'dateNaissance', 'lieuNaissance', 'sexe', 'bureauVote']
                
                # Vérifier si toutes les colonnes nécessaires sont présentes
                if all(field in row for field in required_fields):
                    # Normaliser la structure
                    try:
                        date_str = row['dateNaissance']
                        # Convertir la date au format YYYY-MM-DD si possible
                        date_parts = date_str.split('/')
                        if len(date_parts) == 3:
                            row['dateNaissance'] = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
                        
                        valid_rows.append(row)
                    except Exception as e:
                        row['erreur'] = f"Erreur de format de date: {str(e)}"
                        invalid_rows.append(row)
                else:
                    missing = [field for field in required_fields if field not in row]
                    row['erreur'] = f"Champs manquants: {', '.join(missing)}"
                    invalid_rows.append(row)
    except Exception as e:
        # Si une erreur se produit lors de la lecture, renvoyer ce qui a été traité jusqu'à présent
        pass
        
    return valid_rows, invalid_rows

def has_accents(text: str) -> bool:
    """Vérifie si une chaîne contient des caractères accentués"""
    accent_chars = 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝŸ'
    return any(c in accent_chars for c in text)

def validate_cin_format(cin: str) -> bool:
    """Vérifie si le format de la CIN est valide"""
    return 10 <= len(cin) <= 20 and cin.isalnum()

def validate_electeur_number(num: str) -> bool:
    """Vérifie si le format du numéro d'électeur est valide"""
    return 8 <= len(num) <= 20 and num.isalnum()