# Web-Based Light Scheduler

A real-world IoT dashboard application that allows scheduling light control through a web interface, using WebSocket and MQTT for communication.

## Features

- Web-based interface for scheduling light ON/OFF times
- Real-time communication using WebSocket
- MQTT integration for IoT device control
- Arduino integration for physical light control

## Project Structure

```
.
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── backend/
│   └── websocket_server.py
├── subscriber/
│   └── mqtt_subscriber.py
└── README.md
```

## Prerequisites

- Python 3.8+
- Mosquitto MQTT Broker
- Arduino IDE
- Web Browser

## Installation

1. Install Python dependencies:

```bash
pip install websockets pyserial paho-mqtt
```

2. Install and start Mosquitto MQTT Broker:

```bash
# Windows
# Download and install from https://mosquitto.org/download/
# Start the service

# Linux
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

3. Connect Arduino and upload the provided sketch

## Usage

1. Start the WebSocket server:

```bash
python backend/websocket_server.py
```

2. Start the MQTT subscriber:

```bash
python subscriber/mqtt_subscriber.py
```

3. Open `frontend/index.html` in a web browser

4. Set your desired ON/OFF times and submit the schedule

## Hardware Setup

- Arduino UNO
- Relay module connected to Arduino
- LED or light connected to relay

## License

MIT License
