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

const char* WIFI_SSID   = "Galaxy A51 76DF";
const char* WIFI_PASS   = "Hello.456";
const char* MQTT_BROKER = "10.55.96.175";

#endif
