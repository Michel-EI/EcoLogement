ce répertoire contient la base de données "database.db" le fichier sql "logement.sql" et l'ensemble des codes pythons ainsi que les pages html du sites.

Il y'a aussi des codes Arduino pour les ESP utilisés (ESP32 et ESP8266) pour l'envoie des données de capteurs vers la base et la récupérations de mesures)

Pour lancer le siteweb, il faut lancer le serveur.py qui inclut les bibliothèques suivantes : from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
import httpx
from datetime import datetime, timedelta
import sqlite3
import random
import uvicorn 
import os 

et Pydantic


une fois le serveur lancer pour aller sur la page d'accueil il suffit de taper l'utl suivant:

http://xxx.xxx.x.xxx:8000/ en remplacant biensur les x par votre adresse ip,

une fois à l'accueil vous pourrez naviguer dans les différentes pages, comme décrit dans le fichier txt Partie .

Les différentes routes pour les questions des parties 2 sont dans les codes du serveur (route pour voir la meteo, pour visualiser le graphique des factures etc)


