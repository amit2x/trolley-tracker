#include <Arduino.h>      // Needed explicitly outside the Arduino IDE (PlatformIO/CMake)
#include <NimBLEDevice.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Function prototypes (Arduino IDE auto-generates these; explicit here for plain C++ builds)
void connectWiFi();
void connectMQTT();
void scanBLE();
void sendPing();

// ─── CONFIGURE THESE ───────────────────────────
const char* TROLLEY_ID  = "T-001";
const char* WIFI_SSID   = "Galaxy A51 76DF";
const char* WIFI_PASS   = "Hello.456";
const char* MQTT_BROKER = "10.55.96.175";
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

    WiFi.begin(WIFI_SSID, WIFI_PASS);

    Serial.print("Connecting to WiFi");

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

    while (!mqttClient.connected()) {

        Serial.print("Connecting to MQTT...");

        String clientId = "Trolley-" + String((uint32_t)ESP.getEfuseMac(), HEX);

        if (mqttClient.connect(clientId.c_str())) {

            Serial.println("MQTT Connected!");

        } else {

            Serial.print("Failed rc=");
            Serial.println(mqttClient.state());

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

    // FIX: In NimBLE-Arduino 2.x, NimBLEScan::start() only returns bool
    // (success/failure of starting the scan). The blocking call that
    // returns NimBLEScanResults is now an overload of getResults(),
    // and it takes the duration in MILLISECONDS, not seconds.
    NimBLEScanResults results = scan->getResults(5000, false);

    Serial.println("\n==============================");
    Serial.print("Devices Found: ");
    Serial.println(results.getCount());

    for (int i = 0; i < results.getCount(); i++) {

        const NimBLEAdvertisedDevice* device = results.getDevice(i);

        // FIX: getName() returns std::string in NimBLE 2.x. Use it
        // directly instead of routing through Arduino String, which
        // avoids relying on .c_str() of a temporary.
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

    connectWiFi();

    // Initialize BLE ONLY ONCE
    NimBLEDevice::init("");

    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);

    connectMQTT();
}

//───────────────────────────────────────────────
// Loop
//───────────────────────────────────────────────
void loop() {

    if (!mqttClient.connected()) {

        connectMQTT();
    }

    mqttClient.loop();

    scanBLE();

    sendPing();

    delay(30000);
}