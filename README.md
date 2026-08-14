# 🚀 IoT-Based Airport Trolley Tracking System



An IoT-based indoor trolley tracking system developed during an internship at the **Airports Authority of India (AAI)**. The system uses **ESP32**, **Bluetooth Low Energy (BLE)**, **MQTT**, **Python**, **SQLite**, and **Streamlit** to monitor airport trolley locations in real time.



---



## 📌 Overview



Managing airport trolleys manually is time-consuming and often inefficient. This project demonstrates a prototype that automatically tracks trolley locations within an airport terminal using BLE beacons and ESP32-based trolley scanners.



Each trolley determines its current zone using BLE Received Signal Strength Indicator (RSSI), publishes its location over MQTT, and the backend processes the data before displaying it on a web dashboard for airport staff and passengers.



---



## ✨ Features



- 📡 BLE-based indoor zone detection

- 🚎 ESP32 trolley tracking

- 📶 MQTT-based real-time communication

- 🐍 Python backend for message processing

- 🗄 SQLite database for historical trolley records

- 👨‍💼 Staff dashboard

- ✈ Passenger portal

- 🔒 Secure password authentication using bcrypt

- 🔄 Manual and automatic dashboard refresh

- ⚠ Automatic offline trolley detection

- 📊 Zone-wise trolley monitoring



---



# 🏗 System Architecture



```

ESP32 BLE Beacon

        │

        │ BLE Advertisement

        ▼

ESP32 on Trolley

        │

        │ Wi-Fi + MQTT

        ▼

Mosquitto MQTT Broker

        │

        ▼

Python Backend

        │

        ▼

SQLite Database

        │

        ▼

Streamlit Dashboard

      ├─────────────┐

      ▼             ▼

 Staff Portal   Passenger Portal

```



---



# 🛠 Technology Stack



| Component | Technology |
|-----------|------------|
| Hardware | ESP32 |
| Indoor Positioning | Bluetooth Low Energy (BLE) |
| Communication | MQTT |
| MQTT Broker | Eclipse Mosquitto |
| Backend | Python |
| Database | SQLite |
| Dashboard | Streamlit |
| Authentication | bcrypt |
| JSON Processing | ArduinoJson |
| ESP32 BLE Library | NimBLE-Arduino |


---



# 📂 Project Structure



```text

TROLLEY-TRACKER/

│

├── backend/

│   └── backend.py

│

├── database/

│   ├── database.py

│   ├── setup_users.py

│   ├── add_user.py

│   ├── add_passenger.py

│   ├── reset_password.py

│   ├── current_status.py

│   ├── history_view.py

│   ├── clear_old_data.py

│   └── test.py

│

├── ESP32/

│   ├── beacon/

│   │   └── beacon.ino

│   │

│   └── trolley/

│       ├── trolley.ino

│       ├── secrets.h.example

│       └── secrets.h

│

├── frontend/

│   └── app.py

│

├── shared/

│   ├── auth.py

│   ├── config.py

│   └── __init__.py

│

├── .env.example

├── .env

├── README.md

├── requirements.txt

├── .gitignore

└── trolley.db

```



---



# ⚙ How the System Works



1. ESP32 BLE beacons continuously broadcast unique zone identifiers.

2. ESP32 devices mounted on airport trolleys scan nearby beacons every 30 seconds.

3. The strongest RSSI value determines the trolley's current zone.

4. The trolley creates a JSON message containing:

   - Trolley ID

   - Zone

   - RSSI

5. The JSON message is published to the MQTT topic:



```

airport/trolleys

```



6. Mosquitto forwards the message to the Python backend.

7. The backend:

   - Parses the JSON message

   - Determines trolley status

   - Records the current timestamp

   - Stores the data as a new record in SQLite

8. Every 60 seconds, the backend checks for inactive trolleys and marks them as **OFFLINE** if no updates have been received for more than five minutes.

9. The Streamlit dashboard retrieves the latest record for each trolley and presents it to users.



---



# 📊 Trolley Status Logic



| RSSI | Status |
|------|--------|
| RSSI > -99 | ACTIVE |
| RSSI ≤ -99 | WEAK_SIGNAL |
| RSSI = -999 | OUT_OF_RANGE |
| No update for > 5 minutes | OFFLINE |


---



# 🔐 Authentication



The system provides two separate login portals.



### Staff Portal



- Username

- Password (bcrypt verified)



Features:



- View all tracked trolleys

- Zone filtering

- Active / Weak / Offline counts

- Latest trolley status

- Manual refresh

- Automatic refresh

- Logout



---



### Passenger Portal



Authentication:



- Username

- Passenger Name Record (PNR)



Features:



- Flight information

- Boarding gate

- Scheduled departure time

- Zone selection

- View available ACTIVE trolleys

- Manual refresh

- Automatic refresh

- Logout



---



# 🗄 Database



The application uses **SQLite**.



### trolley_tracking



| Column |
|---------|
| id |
| trolley_id |
| zone |
| rssi |
| status |
| timestamp |


Each MQTT message is stored as a **new database record**, preserving the complete history of trolley movements. The dashboard retrieves the latest record for each trolley when displaying current status.



Additional tables:



- users

- passengers



---



# 🚀 Installation



## 1. Clone the repository



```bash

git clone https://github.com/amit2x/trolley-tracker.git

cd trolley-tracker

```



---



## 2. Install Python dependencies



```bash

pip install -r requirements.txt

```



---



## 3. Configure Environment Variables



Create a `.env` file from `.env.example` and configure:



```text

DB_NAME=trolley.db



MQTT_BROKER=<Broker_IP_Address>

MQTT_PORT=1883

MQTT_TOPIC=airport/trolleys



ADMIN_USERNAME=admin

ADMIN_PASSWORD=admin123

ADMIN_ROLE=admin

```



---



## 4. Configure ESP32 Secrets



Create:



```

ESP32/trolley/secrets.h

```



using:



```

ESP32/trolley/secrets.h.example

```



Configure:



- Wi-Fi SSID

- Wi-Fi Password

- MQTT Broker IP Address



---



## 5. Configure Mosquitto



Add the following to `mosquitto.conf`:



```text

listener 1883 0.0.0.0

allow_anonymous true

```



Restart Mosquitto after saving the configuration.



---



## 6. Initialize the Database



```bash

python database/database.py

python database/setup_users.py

```



---



## 7. Start the Backend



```bash

python backend/backend.py

```



---



## 8. Launch the Dashboard



```bash

streamlit run frontend/app.py

```



---



## 9. Open the Dashboard



```

http://localhost:8501

```



---



# 📈 Results



The prototype successfully demonstrated:



- BLE beacon detection

- Indoor zone identification

- MQTT communication

- End-to-end data transmission

- Historical database logging

- Offline trolley detection

- Staff authentication

- Passenger authentication

- Zone filtering

- Manual refresh

- Non-blocking automatic refresh



---



# 🔮 Future Enhancements



### Hardware



- Deploy tracking units on every airport trolley

- Improve battery life using deep sleep

- GPS support for outdoor areas

- GSM/4G communication

- Rugged enclosures

- Wireless charging



### Software



- Cloud deployment

- PostgreSQL integration

- QR code / boarding pass login

- Push notifications

- Historical analytics

- Mobile application

- Role-based access control

- Integration with Airport Flight Information Display Systems (FIDS)

- Interactive airport map



---



# 📚 References



- ESP32 Technical Reference Manual

- NimBLE-Arduino Documentation

- PubSubClient Documentation

- Eclipse Mosquitto Documentation

- ArduinoJson Documentation

- Eclipse Paho MQTT Python Client

- Streamlit Documentation

- Python Documentation

- SQLite Documentation

- bcrypt Documentation



---



# 📄 License



This project was developed as an academic internship prototype for educational and demonstration purposes.



---



## 👥 Acknowledgement



This project was developed during an internship at the **Airports Authority of India (AAI)** under the guidance of the **IT Department**.
