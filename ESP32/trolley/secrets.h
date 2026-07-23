#ifndef SECRETS_H
#define SECRETS_H

// =====================================================
// secrets.h — local WiFi / MQTT credentials
// =====================================================
// This file is excluded from Git (see .gitignore) so real
// credentials never get committed to the repository.
//
// Copy secrets.h.example to secrets.h and fill in real values
// before uploading trolley.cpp to a device.
// =====================================================

const char* WIFI_SSID   = "";
const char* WIFI_PASS   = "thebrocode";
const char* MQTT_BROKER = "10.32.86.253";

#endif
