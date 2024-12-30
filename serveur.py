from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
import httpx
from datetime import datetime, timedelta
import sqlite3
import random
import uvicorn 
import os 

app = FastAPI() ## instanciation de FastAPI


weather_api_key = "300f58a4bed1428c85e155644242211"  # Clé d'API pour WeatherAPI
## A finir fonction a modifier copier coller
@app.get("/logement")
async def recuperer_logement():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Logement ORDER BY date_insertion DESC LIMIT 1",
        (id,)
    )
    mesure = cursor.fetchone()
    conn.close()

from pydantic import BaseModel
# Classe pour ajouter une nouvelle pièce
class NouvellePiece(BaseModel):
    nom_piece: str
    localisation: str
    nombre_capteur: int
    nombre_actionneur: int
    id_logement: int


class ModifierPiece(BaseModel):
    nom_piece: str
    localisation: str
    nombre_capteur: int
    nombre_actionneur: int

@app.get("/api/capteurs/{id_piece}")
async def recuperer_capteurs(id_piece: int):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id_capteur_actionneur, c.reference_commerciale, t.nom_type AS type_nom
        FROM CapteurActionneur c
        JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
        WHERE c.id_piece = ?
    """, (id_piece,))
    capteurs = cursor.fetchall()
    conn.close()
    return [{"id_capteur_actionneur": c["id_capteur_actionneur"], "reference_commerciale": c["reference_commerciale"], "type_nom": c["type_nom"]} for c in capteurs]

# @app.delete("/api/capteurs/{id_capteur}")
# async def supprimer_capteur(id_capteur: int):
#     conn = db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM CapteurActionneur WHERE id_capteur_actionneur = ?", (id_capteur,))
#     conn.commit()
#     conn.close()
#     return {"message": "Capteur supprimé avec succès"}

    
@app.get("/api/types_capteurs")
async def recuperer_types_capteurs():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_type, nom_type, unite_mesure, plage_precision FROM TypeCapteurActionneur")
    types = cursor.fetchall()
    conn.close()

    # Convertir les résultats en JSON
    return [
        {
            "id_type": type_capteur["id_type"],
            "nom_type": type_capteur["nom_type"],
            "unite_mesure": type_capteur["unite_mesure"],
            "plage_precision": type_capteur["plage_precision"],
        }
        for type_capteur in types
    ]
    
# Modèle pour les données du capteur
class NouveauCapteur(BaseModel):
    id_type: int
    reference_commerciale: str
    id_piece: int
    port_communication: str
    
@app.post("/api/capteurs")
async def ajouter_capteur(capteur: NouveauCapteur):
    conn = db_connection()
    cursor = conn.cursor()

    try:
        # Insérer le capteur dans la base de données
        cursor.execute(
            """
            INSERT INTO CapteurActionneur (id_type, reference_commerciale, id_piece, port_communication)
            VALUES (?, ?, ?, ?)
            """,
            (capteur.id_type, capteur.reference_commerciale, capteur.id_piece, capteur.port_communication)
        )
        conn.commit()
        return {"message": "Capteur ajouté avec succès"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
# pour suppression d un capteur (configuration)
@app.delete("/api/capteurs/{id_capteur}")
async def supprimer_capteur(id_capteur: int):
    print(f"Tentative de suppression du capteur avec ID {id_capteur}")
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM CapteurActionneur WHERE id_capteur_actionneur = ?", (id_capteur,))
        conn.commit()
        return {"message": "Capteur supprimé avec succès"}
    except sqlite3.Error as e:
        return {"message": "Erreur lors de la suppression", "error": str(e)}
    finally:
        conn.close()




@app.get("/api/economies")
async def economies():
    conn = db_connection()
    cursor = conn.cursor()

    # Récupérer les consommations électriques
    cursor.execute("""
        SELECT m.date_insertion AS date, SUM(m.valeur) AS consommation
        FROM Mesure m
        JOIN CapteurActionneur c ON m.id_capteur_actionneur = c.id_capteur_actionneur
        JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
        WHERE t.nom_type = 'Capteur de consommation électrique'
        GROUP BY DATE(m.date_insertion)
        ORDER BY m.date_insertion ASC
    """)
    consommation_electrique = cursor.fetchall()

    # Récupérer les consommations d'eau
    cursor.execute("""
        SELECT m.date_insertion AS date, SUM(m.valeur) AS consommation
        FROM Mesure m
        JOIN CapteurActionneur c ON m.id_capteur_actionneur = c.id_capteur_actionneur
        JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
        WHERE t.nom_type = 'Capteur de consommation eau (volume)'
        GROUP BY DATE(m.date_insertion)
        ORDER BY m.date_insertion ASC
    """)
    consommation_eau = cursor.fetchall()

    conn.close()

    # Générer une courbe de référence (exemple : une consommation réduite de 20%)
    reference_electrique = [
        {"date": record["date"], "reference": record["consommation"] * 0.8}
        for record in consommation_electrique
    ]
    reference_eau = [
        {"date": record["date"], "reference": record["consommation"] * 0.8}
        for record in consommation_eau
    ]

    return {
        "electrique": consommation_electrique,
        "eau": consommation_eau,
        "reference_electrique": reference_electrique,
        "reference_eau": reference_eau,
    }




@app.put("/api/pieces/{id_piece}")
async def modifier_piece(id_piece: int, piece: ModifierPiece):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE Piece
            SET nom_piece = ?, localisation = ?, nombre_capteur = ?, nombre_actionneur = ?
            WHERE id_piece = ?
            """,
            (
                piece.nom_piece,
                piece.localisation,
                piece.nombre_capteur,
                piece.nombre_actionneur,
                id_piece,
            ),
        )
        conn.commit()
        return {"message": "Pièce modifiée avec succès"}
    except sqlite3.Error as e:
        return {"message": "Erreur lors de la modification de la pièce", "error": str(e)}
    finally:
        conn.close()



@app.get("/{page_name}.html", response_class=HTMLResponse)
async def serve_html_page(page_name: str):
    file_path = f"{page_name}.html"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Page non trouvée</h1>", status_code=404)


@app.post("/api/pieces")
async def ajouter_piece(piece: NouvellePiece):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Piece (nom_piece, localisation, nombre_capteur, nombre_actionneur, id_logement)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                piece.nom_piece,
                piece.localisation,
                piece.nombre_capteur,
                piece.nombre_actionneur,
                piece.id_logement,
            ),
        )
        conn.commit()
        return {"message": "Pièce ajoutée avec succès"}
    except sqlite3.Error as e:
        return {"message": "Erreur lors de l'ajout de la pièce", "error": str(e)}
    finally:
        conn.close()



## supresion d'une piece
@app.delete("/api/pieces/{id_piece}")
async def supprimer_piece(id_piece: int):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Piece WHERE id_piece = ?", (id_piece,))
        conn.commit()
        return {"message": "Pièce supprimée avec succès"}
    except sqlite3.Error as e:
        return {"message": "Erreur lors de la suppression de la pièce", "error": str(e)}
    finally:
        conn.close()




## route pour recup les pieces du logement via l'id_logement
@app.get("/api/pieces/{id_logement}")
async def recuperer_pieces(id_logement: int):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_piece, nom_piece, localisation, "
        "COALESCE(nombre_capteur, 0) AS nombre_capteur, "
        "COALESCE(nombre_actionneur, 0) AS nombre_actionneur "
        "FROM Piece WHERE id_logement = ?",
        (id_logement,),
    )
    pieces = cursor.fetchall()
    conn.close()
    return [
        {
            "id_piece": piece["id_piece"],
            "nom_piece": piece["nom_piece"],
            "localisation": piece["localisation"],
            "nombre_capteur": piece["nombre_capteur"],
            "nombre_actionneur": piece["nombre_actionneur"],
        }
        for piece in pieces
    ]



    
@app.get("/api/logements")
async def recuperer_logements():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_logement, adresse, numero_telephone, adresse_ip FROM Logement")
    logements = cursor.fetchall()
    conn.close()

    # Convertir les résultats en JSON
    return [
        {
            "id_logement": logement["id_logement"],
            "adresse": logement["adresse"],
            "numero_telephone": logement["numero_telephone"],
            "adresse_ip": logement["adresse_ip"],
        }
        for logement in logements
    ]

    
# Route pour l'accueil
@app.get("/", response_class=HTMLResponse)
async def accueil():
    with open("Accueil.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


# Route pour la gestion des logements
@app.get("/gestion_logements", response_class=HTMLResponse)
async def gestion_logements():
    with open("gestion_logements.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Route pour toutes les autres pages
@app.get("/{page_name}", response_class=HTMLResponse)
async def serve_page(page_name: str):
    file_path = f"{page_name}.html"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Page non trouvée</h1>", status_code=404)

## recuperation des mesures
@app.get("/mesures/{id_capteur}")
async def recuperer_derniere_mesure(id_capteur: int):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Mesure WHERE id_capteur_actionneur = ? ORDER BY date_insertion DESC LIMIT 1",
        (id_capteur,),
    )
    mesure = cursor.fetchone()
    conn.close()

    if mesure:
        return {
            "id_capteur": mesure["id_capteur_actionneur"],
            "valeur": mesure["valeur"],
            "date_insertion": mesure["date_insertion"],
        }
    else:
        return {"message": "Aucune mesure trouvée pour ce capteur."}

#recup mesures pour site consommation
@app.get("/api/consommation/electrique")
async def consommation_electrique():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.date_insertion, m.valeur
        FROM Mesure m
        INNER JOIN CapteurActionneur c ON m.id_capteur_actionneur = c.id_capteur_actionneur
        INNER JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
        WHERE t.nom_type = 'Capteur de consommation électrique'
        ORDER BY m.date_insertion ASC
    """)
    mesures = cursor.fetchall()
    conn.close()

    return [
        {"date": mesure["date_insertion"], "valeur": mesure["valeur"]}
        for mesure in mesures
    ]

@app.get("/api/consommation/eau")
async def consommation_eau():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.date_insertion, m.valeur
        FROM Mesure m
        INNER JOIN CapteurActionneur c ON m.id_capteur_actionneur = c.id_capteur_actionneur
        INNER JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
        WHERE t.nom_type = 'Capteur de consommation eau (volume)'
        ORDER BY m.date_insertion ASC
    """)
    mesures = cursor.fetchall()
    conn.close()

    return [
        {"date": mesure["date_insertion"], "valeur": mesure["valeur"]}
        for mesure in mesures
    ]



# @app.get("/api/mesures/{id_capteur}")
# async def recuperer_mesures(id_capteur: int):
#     conn = db_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         SELECT valeur, date_insertion 
#         FROM Mesure 
#         WHERE id_capteur_actionneur = ? 
#         ORDER BY date_insertion ASC
#         """,
#         (id_capteur,)
#     )
#     mesures = cursor.fetchall()
#     conn.close()

    # Formater les résultats en JSON
    return [
        {"valeur": mesure["valeur"], "date_insertion": mesure["date_insertion"]}
        for mesure in mesures
    ]



def db_connection():# Connexion à la base de données SQLite
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Fonction pour récupérer tous les capteurs/actionneurs
def recuperer_capteurs():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_capteur_actionneur FROM CapteurActionneur")
    capteurs = cursor.fetchall()
    conn.close()
    return capteurs

@app.get("/api/capteurs")
async def etat_capteurs():
    conn = db_connection()
    cursor = conn.cursor()

    # Récupérer tous les capteurs avec leur type et nombre de mesures
    cursor.execute("""
        SELECT c.id_capteur_actionneur, c.reference_commerciale, t.nom_type, COUNT(m.id_mesure) AS nb_mesures
        FROM CapteurActionneur c
        LEFT JOIN Mesure m ON c.id_capteur_actionneur = m.id_capteur_actionneur
        JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
        GROUP BY c.id_capteur_actionneur
    """)

    capteurs = cursor.fetchall()
    conn.close()

    # Calculer l'état des capteurs
    capteurs_etats = []
    for capteur in capteurs:
        nb_mesures = capteur["nb_mesures"]
        if nb_mesures < 5:
            etat = "Peu de mesures"
            couleur = "green"
        elif 5 <= nb_mesures <= 10:
            etat = "Endommagé"
            couleur = "orange"
        else:
            etat = "État critique"
            couleur = "red"

        capteurs_etats.append({
            "id_capteur_actionneur": capteur["id_capteur_actionneur"],
            "reference_commerciale": capteur["reference_commerciale"],
            "nom_type": capteur["nom_type"],
            "nb_mesures": nb_mesures,
            "etat": etat,
            "couleur": couleur
        })

    return capteurs_etats


    # Formatage des résultats en JSON
    return [
        {
            "id_capteur": capteur["id_capteur_actionneur"],
            "type": capteur["type_capteur"],
            "reference": capteur["reference_commerciale"],
            "piece": capteur["piece"],
            "port": capteur["port_communication"],
            "date_insertion": capteur["date_insertion"]
        }
        for capteur in capteurs
    ]


# Fonction pour ajouter une mesure
def ajouter_mesure(id_capteur, valeur):
    date_mesure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, ?)",
                   (id_capteur, valeur, date_mesure))
    conn.commit()
    conn.close()

# Fonction pour ajouter plusieurs mesures aléatoires
def ajouter_plusieurs_mesures():
    capteurs = recuperer_capteurs()
    for id_capteur in capteurs:
        for _ in range(2):  # Ajouter 2 mesures par capteur
            valeur = round(random.uniform(10, 100), 2)  # Valeur aléatoire
            ajouter_mesure(id_capteur[0], valeur)

# Fonction pour récupérer les données des factures
def recuperer_factures():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type_facture, montant FROM Facture")
    factures = cursor.fetchall()
    conn.close()
    return factures

def verifier_capteur_existe(conn, id_capteur):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM CapteurActionneur WHERE id_capteur_actionneur = ?", (id_capteur,))
    return cursor.fetchone()[0] > 0

def ajouter_capteur(conn, id_capteur):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO CapteurActionneur (id_capteur_actionneur, type, date_insertion) VALUES (?, ?, ?)",
        (id_capteur, "Température", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    
@app.post("/ajouter_donnees")
async def ajouter_donnees(request: Request):
    data = await request.json()
    id_capteur = data.get("id_capteur")
    valeur = data.get("temperature")

    if id_capteur is None or valeur is None:
        return {"message": "Erreur : 'id_capteur' et 'temperature' sont requis."}

    conn = db_connection()

    if not verifier_capteur_existe(conn, id_capteur):
        ajouter_capteur(conn, id_capteur)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, ?)",
        (id_capteur, valeur, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()

    return {"message": "Donnée insérée avec succès"}


# Route GET pour afficher la page HTML avec le graphique
@app.get("/factures", response_class=HTMLResponse)
async def afficher_graphique():
    # Récupérer les données des factures
    factures = recuperer_factures()

    # Formater les données sous forme de tableau JavaScript compatible avec Google Charts
    factures_js = ", ".join([f"['{facture['type_facture']}', {facture['montant']}]"
                             for facture in factures])

    # Lire le contenu du fichier HTML et insérer les données
    with open("graphique.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Remplacer le placeholder {{factures}} dans le HTML par les données formatées
    html_content = html_content.replace("{{factures}}", factures_js)

    return HTMLResponse(content=html_content)

# Fonction pour vérifier l'existence d'une facture
def verifier_facture_existe(id_logement, type_facture, date_facture):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Facture WHERE id_logement = ? AND type_facture = ? AND date_facture = ?",
                   (id_logement, type_facture, date_facture))
    result = cursor.fetchone()
    conn.close()
    return result[0] > 0

# Fonction pour ajouter une facture si elle n'existe pas déjà
def ajouter_facture_si_nouvelle(id_logement, type_facture, montant, valeur_consommation):
    date_facture = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    if not verifier_facture_existe(id_logement, type_facture, date_facture):
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation) VALUES (?, ?, ?, ?, ?)",
                       (id_logement, type_facture, date_facture, montant, valeur_consommation))
        conn.commit()
        conn.close()

# Fonction pour ajouter plusieurs factures
def ajouter_plusieurs_factures():
    id_logement = 1  # Par exemple, le premier logement
    factures = [("Eau", random.uniform(20, 50), random.uniform(10, 30)),
                ("Électricité", random.uniform(50, 100), random.uniform(100, 300)),
                ("Déchets", random.uniform(10, 30), None),
                ("Internet", random.uniform(30, 50), None)]

    for facture in factures:
        ajouter_facture_si_nouvelle(id_logement, facture[0], facture[1], facture[2])

# Route pour récupérer la météo de la ville dynamique
@app.get("/meteo/{ville}", response_class=HTMLResponse)
async def get_meteo(ville: str):
    # URL de l'API avec la ville dynamique
    url = f"http://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={ville}&days=5"
    
    # Effectuer la requête HTTP
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    # Si la réponse est réussie (status 200)
    if response.status_code == 200:
        data = response.json()

        # Récupérer les prévisions pour les 5 jours
        forecast_data = data.get("forecast", {}).get("forecastday", [])

        # Formater les prévisions sous forme de tableau HTML
        forecast_html = "<h1>Prévisions Météo pour {}</h1>".format(ville)
        forecast_html += "<table border='1'><tr><th>Date</th><th>Température (°C)</th><th>Condition</th></tr>"

        for day in forecast_data:
            date = day["date"]
            temp_c = day["day"]["avgtemp_c"]
            condition = day["day"]["condition"]["text"]
            forecast_html += f"<tr><td>{date}</td><td>{temp_c}°C</td><td>{condition}</td></tr>"

        forecast_html += "</table>"
        return HTMLResponse(content=forecast_html)
    else:
        return HTMLResponse(content="<h1>Erreur lors de la récupération des données météo.</h1>")

# Pour démarrer le serveur FastAPI, exécutez la commande suivante:
# uvicorn serveur:app --reload

if __name__ == "__main__":
    #uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)

