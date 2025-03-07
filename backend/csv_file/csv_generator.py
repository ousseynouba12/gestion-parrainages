import csv
import random
from datetime import datetime, timedelta

# Fonction pour nettoyer les caractères non compatibles avec Latin-1
def nettoyer_pour_latin1(texte):
    # Remplacer les caractères qui posent problème
    mapping = {
        'Œ': 'OE', 'œ': 'oe',
        'É': 'E', 'é': 'e',
        'È': 'E', 'è': 'e',
        'Ê': 'E', 'ê': 'e',
        'Ë': 'E', 'ë': 'e',
        'À': 'A', 'à': 'a',
        'Â': 'A', 'â': 'a',
        'Î': 'I', 'î': 'i',
        'Ï': 'I', 'ï': 'i',
        'Ô': 'O', 'ô': 'o',
        'Ù': 'U', 'ù': 'u',
        'Û': 'U', 'û': 'u',
        'Ü': 'U', 'ü': 'u',
        'Ç': 'C', 'ç': 'c',
        'Ñ': 'N', 'ñ': 'n'
    }
    for char, replacement in mapping.items():
        texte = texte.replace(char, replacement)
    return texte

# Données étendues pour représenter la diversité du Sénégal
BUREAUX_VOTE = [
    # Dakar
    'ECOLE MARIAMA NIASS - GRAND DAKAR',
    'LYCEE SEYDOU NOUROU TALL - PLATEAU',
    'ECOLE POINT E - FANN',
    'ECOLE ELEMENTAIRE HLM GRAND MEDINE',
    'LYCEE LIMAMOULAYE - GUEDIAWAYE',
    'COLLEGE SACRE-COEUR - DAKAR',
    # Thiès
    'ECOLE ELEMENTAIRE RANDOULENE - THIES',
    'LYCEE MALICK SY - THIES',
    'CENTRE CULTUREL - THIES',
    # Saint-Louis
    'ECOLE ELEMENTAIRE CHEIKH TOURE - SAINT-LOUIS',
    'UNIVERSITE GASTON BERGER - SAINT-LOUIS',
    'ECOLE ELEMENTAIRE BANGO - SAINT-LOUIS',
    # Ziguinchor
    'ECOLE NEMA - ZIGUINCHOR',
    'LYCEE DJIGNABO - ZIGUINCHOR',
    'ECOLE SAINT JOSEPH - ZIGUINCHOR',
    # Diourbel
    'ECOLE ELEMENTAIRE DIOURBEL CENTRE',
    'LYCEE MBACKE - TOUBA',
    'ECOLE COMMUNALE DE NDOULO',
    # Kaolack
    'ECOLE SERIGNE BASSIROU MBACKE - KAOLACK',
    'LYCEE VALDIODIO NDIAYE - KAOLACK',
    'ECOLE ELEMENTAIRE MEDINA BAYE',
    # Fatick
    'ECOLE SAMBA NDIAYE - FATICK',
    'COLLEGE PRIVE DE FATICK',
    'ECOLE ELEMENTAIRE DIAKHAO',
    # Louga
    'ECOLE ELEMENTAIRE LOUGA NORD',
    'LYCEE MALICK SALL - LOUGA',
    'ECOLE PRIMAIRE DE KEBEMER',
    # Tambacounda
    'LYCEE MAME CHEIKH MBAYE - TAMBACOUNDA',
    'ECOLE ELEMENTAIRE TAMBACOUNDA CENTRE',
    'ECOLE COMMUNALE DE BAKEL',
    # Kolda
    'ECOLE ELEMENTAIRE SIKILO - KOLDA',
    'LYCEE TANK - KOLDA',
    'ECOLE PRIMAIRE DE VELINGARA',
    # Matam
    'LYCEE DE MATAM',
    'ECOLE ELEMENTAIRE OUROSSOGUI',
    'ECOLE COMMUNALE DE KANEL',
    # Kaffrine
    'ECOLE ELEMENTAIRE KAFFRINE CENTRE',
    'LYCEE DE KOUNGHEUL',
    'ECOLE PRIMAIRE DE BIRKELANE',
    # Kédougou
    'LYCEE DE KEDOUGOU',
    'ECOLE ELEMENTAIRE BANDAFASSI',
    'ECOLE PRIMAIRE DE SALEMATA',
    # Sédhiou
    'ECOLE ELEMENTAIRE SEDHIOU CENTRE',
    'LYCEE DEPARTEMENTAL DE SEDHIOU',
    'ECOLE PRIMAIRE DE GOUDOMP'
]

NOMS = [
    'DIOP', 'NDIAYE', 'SALL', 'FALL', 'GUEYE', 'BA', 'DIOUF', 'SOW', 'DIALLO',
    'MBAYE', 'THIAM', 'NIANG', 'SY', 'SARR', 'CISSE', 'NDAO', 'MBENGUE', 'FAYE',
    'CAMARA', 'LY', 'SECK', 'TOURE', 'WADE', 'KA', 'DIAGNE', 'DIARRA', 'DIA',
    'LO', 'SAMB', 'BADJI', 'SANE', 'GOMIS', 'DIONE', 'SEYDI', 'MBODJ', 'NDONG'
]

# Version sans accents pour Latin-1
PRENOMS_LATIN1 = [
    'Abdoulaye', 'Mamadou', 'Fatou', 'Aminata', 'Ibrahima', 'Ousmane', 'Aissatou',
    'Moussa', 'Seynabou', 'Modou', 'Mariama', 'Omar', 'Astou', 'Cheikh', 'Mame',
    'Awa', 'Oumar', 'Rokhaya', 'Samba', 'Khady', 'Malick', 'Ramatoulaye', 'Pape',
    'Daba', 'Boubacar', 'Ndeye', 'Demba', 'Sokhna', 'Aliou', 'Maguette', 'Fode',
    'Coumba', 'Babacar', 'Rama', 'Fallou', 'Binta', 'Idrissa', 'Dieynaba', 'Mansour'
]

# Version avec accents pour UTF-8
PRENOMS_UTF8 = [
    'Abdoulaye', 'Mamadou', 'Fatou', 'Aminata', 'Ibrahima', 'Ousmane', 'Aïssatou',
    'Moussa', 'Seynabou', 'Modou', 'Mariama', 'Omar', 'Astou', 'Cheikh', 'Mame',
    'Awa', 'Oumar', 'Rokhaya', 'Samba', 'Khady', 'Malick', 'Ramatoulaye', 'Pape',
    'Daba', 'Boubacar', 'Ndeye', 'Demba', 'Sokhna', 'Aliou', 'Maguette', 'Fodé',
    'Coumba', 'Babacar', 'Rama', 'Fallou', 'Binta', 'Idrissa', 'Dieynaba', 'Mansour'
]

# Version sans accents pour Latin-1
LIEUX_LATIN1 = [
    'DAKAR', 'THIES', 'SAINT-LOUIS', 'RUFISQUE', 'ZIGUINCHOR', 'KAOLACK',
    'TOUBA', 'MBOUR', 'DIOURBEL', 'LOUGA', 'TAMBACOUNDA', 'KOLDA', 'MATAM',
    'FATICK', 'PIKINE', 'GUEDIAWAYE', 'KAFFRINE', 'KEDOUGOU', 'SEDHIOU', 'JOAL',
    'DAGANA', 'PODOR', 'TIVAOUANE', 'LINGUERE', 'MBACKE', 'BAKEL', 'VELINGARA',
    'KEBEMER', 'GOSSAS', 'BAMBEY', 'KOUNGHEUL', 'NIORO DU RIP', 'NDIOUM', 'MEKHE'
]

# Version avec accents pour UTF-8
LIEUX_UTF8 = [
    'DAKAR', 'THIÈS', 'SAINT-LOUIS', 'RUFISQUE', 'ZIGUINCHOR', 'KAOLACK',
    'TOUBA', 'MBOUR', 'DIOURBEL', 'LOUGA', 'TAMBACOUNDA', 'KOLDA', 'MATAM',
    'FATICK', 'PIKINE', 'GUÉDIAWAYE', 'KAFFRINE', 'KÉDOUGOU', 'SÉDHIOU', 'JOAL',
    'DAGANA', 'PODOR', 'TIVAOUANE', 'LINGUÈRE', 'MBACKÉ', 'BAKEL', 'VÉLINGARA',
    'KÉBÉMER', 'GOSSAS', 'BAMBEY', 'KOUNGHEUL', 'NIORO DU RIP', 'NDIOUM', 'MÉKHÉ'
]

def generer_cin_valide():
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

def generer_numero_electeur_valide():
    lettres = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3)])
    chiffres = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{lettres}{chiffres}"

def generer_date_naissance():
    aujourd_hui = datetime.now()
    age = random.randint(18 * 365, 90 * 365)  # Entre 18 et 90 ans
    date_naissance = aujourd_hui - timedelta(days=age)
    return date_naissance.strftime('%Y-%m-%d')

# Création des données pour le fichier Latin-1 (sans accents)
donnees_latin1 = [
    ['numElecteur', 'numCIN', 'nom', 'prenom', 'dateNaissance', 'lieuNaissance', 'sexe', 'bureauVote']
]

# Génération de 200 électeurs valides pour Latin-1
for _ in range(200):
    electeur = [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        random.choice(NOMS),
        random.choice(PRENOMS_LATIN1),
        generer_date_naissance(),
        random.choice(LIEUX_LATIN1),
        random.choice(['M', 'F']),
        random.choice(BUREAUX_VOTE)
    ]
    donnees_latin1.append(electeur)

# Création des données pour le fichier UTF-8 avec électeurs invalides
donnees_utf8 = [
    ['numElecteur', 'numCIN', 'nom', 'prenom', 'dateNaissance', 'lieuNaissance', 'sexe', 'bureauVote']
]

# 200 électeurs valides pour UTF-8 (avec accents)
for _ in range(200):
    electeur = [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        random.choice(NOMS),
        random.choice(PRENOMS_UTF8),
        generer_date_naissance(),
        random.choice(LIEUX_UTF8),
        random.choice(['M', 'F']),
        random.choice(BUREAUX_VOTE)
    ]
    donnees_utf8.append(electeur)

# Ajout d'électeurs invalides pour le fichier UTF-8
electeurs_invalides = [
    # CIN invalide (trop court)
    [
        generer_numero_electeur_valide(),
        '12345',
        'DIOP',
        'Mamadou',
        '1990-01-01',
        'DAKAR',
        'M',
        BUREAUX_VOTE[0]
    ],
    # Numéro électeur invalide (format incorrect)
    [
        'ABC12',
        generer_cin_valide(),
        'NDIAYE',
        'Fatou',
        '1985-05-15',
        'THIÈS',
        'F',
        BUREAUX_VOTE[1]
    ],
    # Mineur
    [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        'SALL',
        'Omar',
        '2010-03-20',
        'DAKAR',
        'M',
        BUREAUX_VOTE[2]
    ],
    # Sexe invalide
    [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        'BA',
        'Aïssatou',
        '1995-11-30',
        'SAINT-LOUIS',
        'X',
        BUREAUX_VOTE[0]
    ],
    # Bureau invalide
    [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        'GUEYE',
        'Abdoulaye',
        '1988-07-22',
        'RUFISQUE',
        'M',
        'BUREAU INEXISTANT'
    ],
    # CIN déjà utilisée (doublon)
    [
        generer_numero_electeur_valide(),
        donnees_utf8[1][1],  # Utilise la CIN du premier électeur
        'MBAYE',
        'Sokhna',
        '1979-12-05',
        'MBOUR',
        'F',
        BUREAUX_VOTE[5]
    ],
    # Numéro d'électeur déjà utilisé
    [
        donnees_utf8[2][0],  # Utilise le numéro d'électeur du deuxième électeur
        generer_cin_valide(),
        'DIALLO',
        'Modou',
        '1982-08-17',
        'TOUBA',
        'M',
        BUREAUX_VOTE[8]
    ],
    # Date de naissance manquante
    [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        'THIAM',
        'Ramatoulaye',
        '',
        'KAOLACK',
        'F',
        BUREAUX_VOTE[10]
    ],
    # Nom manquant
    [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        '',
        'Cheikh',
        '1975-04-10',
        'LOUGA',
        'M',
        BUREAUX_VOTE[12]
    ],
    # Lieu de naissance manquant
    [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        'NDAO',
        'Dieynaba',
        '1991-09-25',
        '',
        'F',
        BUREAUX_VOTE[15]
    ]
]

donnees_utf8.extend(electeurs_invalides)

# Écriture des fichiers avec les bons encodages et gestion des caractères spéciaux
with open('electeurs_latin1.csv', 'w', encoding='latin1', newline='') as f:
    writer = csv.writer(f)
    for ligne in donnees_latin1:
        # Nettoyage des données pour la compatibilité Latin-1
        ligne_propre = [nettoyer_pour_latin1(str(item)) if isinstance(item, str) else item for item in ligne]
        writer.writerow(ligne_propre)

# Écriture explicite en UTF-8 avec BOM pour garantir la reconnaissance de l'encodage
with open('electeurs_utf8_avec_invalides.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(donnees_utf8)

print(f"Génération terminée :")
print(f"- {len(donnees_latin1) - 1} électeurs valides dans 'electeurs_latin1.csv' (encodage Latin-1)")
print(f"- {len(donnees_utf8) - 1} électeurs (dont {len(electeurs_invalides)} invalides) dans 'electeurs_utf8_avec_invalides.csv' (encodage UTF-8)")
print(f"- {len(BUREAUX_VOTE)} bureaux de vote répartis dans toutes les régions du Sénégal")