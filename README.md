# RiceMaid

**Smart Rice Farming Management Platform**

RiceMaid is a comprehensive agricultural technology platform designed to help Thai rice farmers optimize their farming practices using IoT sensors, AI-powered insights, and carbon credit calculations. Built for the Ideathon project, this system integrates real-time field monitoring, rice growth stage prediction, and an intelligent LINE chatbot assistant.

## 🌾 Features

### 🤖 AI-Powered LINE Chatbot
- **Rice Farming Assistant**: Conversational AI (Google Gemini) that provides farming advice and answers agricultural questions
- **Rice Growth Stage Detection**: Upload photos to identify rice growth stages (BBCH11-กล้า, BBCH12-ยืดปล้อง, BBCH13-ตั้งท้อง) using TensorFlow EfficientNetB3
- **Carbon Credit Calculator**: Interactive calculation of methane emissions and carbon credits based on field area and harvest age
- **Water Resource Reports**: Real-time water data from Thailand's Department of Water Resources API by province
- **Farm News**: Daily agricultural news aggregation via Tavily search API
- **Field Overview**: Comprehensive reports on water levels, soil moisture, weather, and environmental conditions
- **Smart Recommendations**: Context-aware farming advice based on IoT data, weather, and user inputs

### 📡 IoT Integration
- **ESP32-based Sensors**:
  - Soil moisture and temperature monitoring (MQTT protocol)
  - Ultrasonic water level sensors
  - Real-time data streaming to backend via MQTT
- **Field Monitoring**:
  - Track soil moisture levels (dry/wet/optimal)
  - Monitor temperature with automatic alerts
  - Water level tracking across fields
  - Historical data queries by device ID and time range

### 🌍 Carbon Credit System
- Calculate methane emissions from rice paddies
- Estimate carbon credits based on field size and harvest duration
- Support for Alternate Wetting and Drying (AWD) farming practices

### 🔐 User Authentication
- JWT-based authentication with access and refresh tokens
- Secure user registration and password management
- Protected API endpoints

### 🗃️ Database Models
- User accounts and authentication
- LINE user profiles with province information
- Field water level measurements
- Field statistics (soil moisture, temperature, status)
- Refresh token management

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **ML/AI**: 
  - TensorFlow 2.18 (EfficientNetB3 for image classification)
  - Google Generative AI (Gemini 1.5 Flash)
- **IoT**: MQTT protocol with ESP32 microcontrollers
- **External APIs**:
  - LINE Messaging API (chatbot interface)
  - Thailand Water Resources API
  - Tavily Search API
  - Google Vertex AI
- **DevOps**: Docker, Docker Compose, Alembic migrations
- **Testing**: Pytest with 100% coverage requirement

## 📦 Installation

### Prerequisites
- Python 3.12+
- Poetry
- Docker & Docker Compose
- PostgreSQL (via Docker)

### Setup

1. Install dependencies:

```bash
poetry install
```

2. Start PostgreSQL database:

```bash
docker-compose up -d
```

3. Run database migrations:

```bash
alembic upgrade head
```

4. Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

5. (Optional) Expose local server for LINE webhook:

```bash
ngrok http 8000 --host-header="127.0.0.1:8000"
```

The API documentation will be available at `http://localhost:8000/`

## 🚀 API Endpoints

- `/auth/*` - User authentication (register, login, refresh token, password reset)
- `/api/v1/users/*` - User management
- `/api/v1/predictions/predict` - Rice growth stage image prediction
- `/api/v1/carbon-credit/` - Carbon credit calculations
- `/api/v1/iot/water-level/*` - Water level data management
- `/api/v1/iot/field-stats/*` - Field statistics management
- `/api/v1/line/webhook` - LINE messaging webhook handler

## 🌐 IoT Deployment

The `iot/` directory contains ESP32 firmware for:
- **ESP32mqttSoilTemp**: Soil moisture and temperature sensor with LCD display
- **ESP32mqttUltraSonic**: Water level monitoring using ultrasonic sensors

Both devices communicate via MQTT and can be simulated on Wokwi.

## 📊 ML Model

The rice growth stage classifier uses:
- **Architecture**: EfficientNetB3 with custom classification head
- **Classes**: BBCH11 (seedling), BBCH12 (tillering), BBCH13 (booting)
- **Input**: 300x300 RGB images
- **Weights**: Pre-trained on ImageNet, fine-tuned for rice growth stages

## 📝 Testing

Run the test suite:

```bash
pytest
```

The project maintains 100% code coverage across all modules.

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This project was developed for the Ideathon competition to support sustainable rice farming practices in Thailand.
