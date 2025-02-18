import csv
import random
from datetime import datetime, timedelta

# Données de test avec caractères spéciaux correctement définis
BUREAUX_VOTE = [
    'ÉCOLE MARIAMA NIASS - GRAND DAKAR',
    'LYCÉE SEYDOU NOUROU TALL - PLATEAU',
    'ÉCOLE POINT E - FANN'
]

NOMS = ['DIOP', 'NDIAYE', 'SALL', 'FALL', 'GUEYE']
PRENOMS = ['Abdoulaye', 'Mamadou', 'Fatou', 'Aminata', 'Ibrahima']
LIEUX = ['DAKAR', 'THIÈS', 'SAINT-LOUIS', 'RUFISQUE']

def generer_cin_valide():
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

def generer_numero_electeur_valide():
    lettres = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3)])
    chiffres = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{lettres}{chiffres}"

def generer_date_naissance():
    aujourd_hui = datetime.now()
    age = random.randint(18 * 365, 90 * 365)
    date_naissance = aujourd_hui - timedelta(days=age)
    return date_naissance.strftime('%Y-%m-%d')

# Création des données pour le fichier Latin-1
donnees_latin1 = [
    ['numElecteur', 'numCIN', 'nom', 'prenom', 'dateNaissance', 'lieuNaissance', 'sexe', 'bureauVote']
]

for _ in range(10):
    electeur = [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        random.choice(NOMS),
        random.choice(PRENOMS),
        generer_date_naissance(),
        random.choice(LIEUX),
        random.choice(['M', 'F']),
        random.choice(BUREAUX_VOTE)
    ]
    donnees_latin1.append(electeur)

# Création des données pour le fichier UTF-8 avec électeurs invalides
donnees_utf8 = [
    ['numElecteur', 'numCIN', 'nom', 'prenom', 'dateNaissance', 'lieuNaissance', 'sexe', 'bureauVote']
]

# 10 électeurs valides
for _ in range(10):
    electeur = [
        generer_numero_electeur_valide(),
        generer_cin_valide(),
        random.choice(NOMS),
        random.choice(PRENOMS),
        generer_date_naissance(),
        random.choice(LIEUX),
        random.choice(['M', 'F']),
        random.choice(BUREAUX_VOTE)
    ]
    donnees_utf8.append(electeur)

# Ajout d'électeurs invalides pour le fichier UTF-8
electeurs_invalides = [
    # CIN invalide
    [
        generer_numero_electeur_valide(),
        '12345',  # CIN trop court
        'DIOP',
        'Mamadou',
        '1990-01-01',
        'DAKAR',
        'M',
        BUREAUX_VOTE[0]
    ],
    # Numéro électeur invalide
    [
        'ABC12',  # Numéro électeur invalide
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
    ]
]

donnees_utf8.extend(electeurs_invalides)

# Écriture des fichiers avec les bons encodages
with open('electeurs_latin1.csv', 'w', encoding='latin1', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(donnees_latin1)

# Écriture explicite en UTF-8 avec BOM pour garantir la reconnaissance de l'encodage
with open('electeurs_utf8_avec_invalides.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(donnees_utf8)
