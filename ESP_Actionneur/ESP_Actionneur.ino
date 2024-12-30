#include <WiFi.h>
#include <HTTPClient.h>

// Informations Wi-Fi
const char* ssid = "Bath-man";       
const char* password = "XavierDupont"; 

// URL du serveur FastAPI
const char* serverURL = "http://192.168.40.2:8000/mesures/1"; 

// Pin de la LED (ou autre actionneur)
const int ledPin = 2; // GPIO2 sur ESP32

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

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

    // Récupération des données depuis le serveur
    http.begin(serverURL);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Réponse du serveur : " + response);

      // Analyse des données (exemple simple : recherche de la valeur)
      int valeurIndex = response.indexOf("\"valeur\":") + 9;
      float valeur = response.substring(valeurIndex).toFloat();

      // Action sur la LED (par exemple, si température > 30)
      if (valeur > 25.0) {
        digitalWrite(ledPin, HIGH); // Allumer la LED
      } else {
        digitalWrite(ledPin, LOW); // Éteindre la LED
      }
    } else {
      Serial.println("Erreur lors de la récupération des données : " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("WiFi déconnecté");
  }

  delay(5000); // Pause avant la prochaine récupération
}
