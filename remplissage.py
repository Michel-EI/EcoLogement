import sqlite3
import random
from datetime import datetime, timedelta

# Connexion à la base de données
conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row
curseur = conn.cursor()

# Fonction pour récupérer tous les capteurs/actionneurs
def recuperer_capteurs():
    curseur.execute("SELECT id_capteur_actionneur FROM CapteurActionneur")
    return [ligne["id_capteur_actionneur"] for ligne in curseur.fetchall()]

# Fonction pour ajouter une mesure
def ajouter_mesure(id_capteur, valeur):
    date_mesure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    curseur.execute("INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, ?)",(id_capteur, valeur, date_mesure))

# Fonction pour ajouter plusieurs mesures aléatoires
def ajouter_plusieurs_mesures():
    capteurs = recuperer_capteurs()
    for id_capteur in capteurs:
        for _ in range(2):  # Ajouter 2 mesures par capteur
            valeur = round(random.uniform(10, 100), 2)  # Valeur aléatoire
            ajouter_mesure(id_capteur, valeur)

# Fonction pour vérifier l'existence d'une facture
def verifier_facture_existe(id_logement, type_facture, date_facture):
    curseur.execute("SELECT COUNT(*) FROM Facture WHERE id_logement = ? AND type_facture = ? AND date_facture = ?",(id_logement, type_facture, date_facture))
    return curseur.fetchone()[0] > 0

# Fonction pour ajouter une facture si elle n'existe pas déjà
def ajouter_facture_si_nouvelle(id_logement, type_facture, montant, valeur_consommation):
    date_facture = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    montant = round(montant, 2)  # Arrondir le montant à 2 décimales
    if not verifier_facture_existe(id_logement, type_facture, date_facture):
        curseur.execute("INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation) VALUES (?, ?, ?, ?, ?)",(id_logement, type_facture, date_facture, montant, valeur_consommation))
        print(f"Facture ajoutée : {type_facture}, Montant : {montant}, Date : {date_facture}")
    else:
        print(f"Facture déjà présente : {type_facture}, Date : {date_facture}")

# Fonction pour ajouter plusieurs factures
def ajouter_plusieurs_factures():
    id_logement = 1  # Par exemple, le premier logement
    factures = [
        ("Eau", random.uniform(20, 50), random.uniform(10, 30)),
        ("Électricité", random.uniform(50, 100), random.uniform(100, 300)),
        ("Déchets", random.uniform(10, 30), None),
        ("Internet", random.uniform(30, 50), None),
    ]
    for facture in factures:
        ajouter_facture_si_nouvelle(id_logement, facture[0], facture[1], facture[2])

# Appel des fonctions pour insérer les données
ajouter_plusieurs_mesures()  # Ajouter plusieurs mesures pour tous les capteurs
ajouter_plusieurs_factures()  # Ajouter plusieurs factures

# Sauvegarde et fermeture de la base de données
conn.commit()
conn.close()
