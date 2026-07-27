#include <NimBLEDevice.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"   // WIFI_SSID, WIFI_PASS, MQTT_BROKER — never committed, see secrets.h

// Function prototypes (Arduino IDE auto-generates these; explicit here for plain C++ builds)
void connectWiFi();
void connectMQTT();
void scanBLE();
void sendPing();

// ─── CONFIGURE THESE ───────────────────────────
// WIFI_SSID, WIFI_PASS, and MQTT_BROKER now live in secrets.h so that
// real credentials are never hard-coded here or committed to Git.
const char* TROLLEY_ID  = "T-001";
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "airport/trolleys";

// Known Beacons
struct Beacon {
    const char* name;
    const char* zone;
};

Beacon knownBeacons[] = {
    {"ZONE_A_BEACON", "ZONE_A"},
    {"ZONE_B_BEACON", "ZONE_B"},
    {"ZONE_C_BEACON", "ZONE_C"},
};

int beaconCount = 3;

// MQTT
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Current Zone
String bestZone = "UNKNOWN";
int bestRSSI = -999;

//───────────────────────────────────────────────
// WIFI
//───────────────────────────────────────────────
void connectWiFi() {

    // Already connected, nothing to do.
    if (WiFi.status() == WL_CONNECTED)
        return;

    Serial.print("Connecting to WiFi");

    // Start a fresh WiFi connection attempt.
    WiFi.disconnect(true);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    // Wait until the ESP32 successfully reconnects.
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi Connected!");

    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    Serial.print("Gateway IP: ");
    Serial.println(WiFi.gatewayIP());
}

//───────────────────────────────────────────────
// MQTT
//───────────────────────────────────────────────
void connectMQTT() {

    // Keep retrying until the MQTT broker becomes available.
    // This provides automatic MQTT reconnection if the broker
    // is restarted or the connection is temporarily lost.
    while (!mqttClient.connected()) {

        Serial.print("Connecting to MQTT...");

        String clientId = "Trolley-" + String((uint32_t)ESP.getEfuseMac(), HEX);

        if (mqttClient.connect(clientId.c_str())) {

            Serial.println("MQTT Connected!");

        } else {

            Serial.print("Failed rc=");
            Serial.println(mqttClient.state());

            // Wait before retrying to avoid flooding the broker.
            delay(2000);
        }
    }
}

//───────────────────────────────────────────────
// BLE Scan
//───────────────────────────────────────────────
void scanBLE() {

    bestZone = "UNKNOWN";
    bestRSSI = -999;

    NimBLEScan* scan = NimBLEDevice::getScan();

    scan->setActiveScan(true);
    scan->setInterval(100);
    scan->setWindow(90);

    NimBLEScanResults results = scan->getResults(5000, false);

    Serial.println("\n==============================");
    Serial.print("Devices Found: ");
    Serial.println(results.getCount());

    for (int i = 0; i < results.getCount(); i++) {

        const NimBLEAdvertisedDevice* device = results.getDevice(i);

        std::string name = device->getName();
        int rssi = device->getRSSI();

        Serial.print("Device: ");
        Serial.print(name.c_str());

        Serial.print(" | RSSI: ");
        Serial.println(rssi);

        for (int j = 0; j < beaconCount; j++) {

            if (name == knownBeacons[j].name) {

                Serial.println("***** BEACON DETECTED *****");

                if (rssi > bestRSSI) {

                    bestRSSI = rssi;
                    bestZone = knownBeacons[j].zone;
                }
            }
        }
    }

    scan->clearResults();

    Serial.print("Current Zone: ");
    Serial.println(bestZone);

    Serial.print("Best RSSI: ");
    Serial.println(bestRSSI);
}

//───────────────────────────────────────────────
// Publish MQTT
//───────────────────────────────────────────────
void sendPing() {

    // Publish only when the MQTT connection is active.
    if (!mqttClient.connected()) {
        Serial.println("MQTT not connected. Publish skipped.");
        return;
    }

    StaticJsonDocument<200> doc;

    doc["trolley_id"] = TROLLEY_ID;
    doc["zone"] = bestZone;
    doc["rssi"] = bestRSSI;

    char jsonBuffer[200];

    serializeJson(doc, jsonBuffer);

    mqttClient.publish(MQTT_TOPIC, jsonBuffer);

    Serial.print("Published: ");
    Serial.println(jsonBuffer);
}

//───────────────────────────────────────────────
// Setup
//───────────────────────────────────────────────
void setup() {

    Serial.begin(115200);

    delay(1000);

    Serial.println("Trolley Tracker Starting...");

    // Enable the ESP32's built-in WiFi auto-reconnect feature.
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);

    // Establish the initial WiFi connection.
    connectWiFi();

    // Initialize BLE ONLY ONCE.
    NimBLEDevice::init("");

    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);

    // Establish the initial MQTT connection.
    connectMQTT();
}

//───────────────────────────────────────────────
// Loop
//───────────────────────────────────────────────
void loop() {

    // Automatically reconnect to WiFi if the connection is lost.
    if (WiFi.status() != WL_CONNECTED) {

        Serial.println("WiFi disconnected. Reconnecting...");

        connectWiFi();
    }

    // Automatically reconnect to the MQTT broker if the
    // MQTT session is lost (e.g., broker restart or network interruption).
    if (!mqttClient.connected()) {

        Serial.println("MQTT disconnected. Reconnecting...");

        connectMQTT();
    }

    // Maintain the MQTT connection and process keep-alive packets.
    mqttClient.loop();

    scanBLE();

    sendPing();

    // Send an update every 30 seconds.
    delay(30000);
}