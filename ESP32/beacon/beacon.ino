#include <NimBLEDevice.h>

// =============================
// CHANGE THIS FOR EACH BEACON
// =============================
const char* BEACON_NAME = "ZONE_A_BEACON";

NimBLEAdvertising* pAdvertising;

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("=================================");
    Serial.println("ESP32 Beacon Starting");
    Serial.print("Beacon Name: ");
    Serial.println(BEACON_NAME);

    // Initialize BLE
    NimBLEDevice::init(BEACON_NAME);

    // Create advertising object
    pAdvertising = NimBLEDevice::getAdvertising();

    // Create advertising packet
    NimBLEAdvertisementData advData;
    advData.setName(BEACON_NAME);
    advData.setFlags(0x06);

    pAdvertising->setAdvertisementData(advData);

    // Put the name in the scan response too
    NimBLEAdvertisementData scanData;
    scanData.setName(BEACON_NAME);
    pAdvertising->setScanResponseData(scanData);

    // Start advertising
    pAdvertising->start();

    Serial.println("Beacon is broadcasting...");
    Serial.println("=================================");
}

void loop() {
    delay(1000);
}