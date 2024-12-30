#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "DHT.h"

// Type de capteur et broche
#define DHTTYPE DHT11
#define DHTPIN D3 // GPIO0 sur NodeMCU
DHT dht(DHTPIN, DHTTYPE);

// Informations Wi-Fi
const char* ssid = "Bath-man";     
const char* password = "XavierDupont";  

// URL du serveur FastAPI
const char* serverURL = "http://192.168.40.2:8000/ajouter_donnees"; // Remplacez par l'adresse IP de votre serveur

WiFiClient wifiClient;

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Connexion au Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connexion au WiFi...");
  }
  Serial.println("Connecté au WiFi");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Lecture des données du capteur
    float temperature = dht.readTemperature();

    // Vérification des données
    if (isnan(temperature)) {
      Serial.println("Erreur de lecture du capteur de température.");
      delay(2000);
      return;
    }

    // Création du message JSON pour la température
    String jsonMessage = "{\"id_capteur\": 1, \"temperature\": " + String(temperature) + "}";

    // Envoi de la requête POST
    http.begin(wifiClient, serverURL);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonMessage);

    // Affichage des résultats
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Code réponse: " + String(httpResponseCode));
      Serial.println("Réponse: " + response);
    } else {
      Serial.println("Erreur lors de l'envoi des données.");
    }

    // Fin de la requête
    http.end();
  } else {
    Serial.println("WiFi déconnecté");
  }

  // Pause avant la prochaine lecture
  delay(10000);
}
