# AI Predictive Maintenance Dashboard

## Overview
An AI-powered predictive maintenance system that detects industrial equipment faults, tracks real-time sensor metrics, provides optimized scheduling actions, and generates dynamic recommendations via LLM integrations.

## Features
- **Fault Prediction**: Machine Learning-based classification of equipment state.
- **AI Recommendation Engine**: Streams real-time diagnostic actions using Gemini/Azure OpenAI.
- **Maintenance Scheduler**: Calculates optimized servicing timeframes based on fault states.
- **Real-Time Sensor Monitoring**: Interactive live telemetry dashboard using Chart.js.
- **Token-Based RBAC Access Controls**: Secured technician, engineer, and reliability engineer view scopes with Flask endpoints protected by authentication hooks and rate-limit controls.
- **Equipment Health Alerts**: Automatic warning dispatches using SMTP Email and Twilio SMS.

## Technologies Used
### Frontend
- HTML5 & CSS3 (Vanilla Glassmorphism UI)
- JavaScript (Vanilla Fetch & SSE Streams)
- Chart.js (Real-time telemetry and contribution breakdown charts)
- FontAwesome Icons

### Backend & AI
- Python
- Flask & Flask-CORS
- itsdangerous (Cryptographic session token serialization)
- Scikit-Learn (RandomForest Classifier ML model)
- Pandas & NumPy
- Joblib (Model persistence)
- google-generativeai SDK / Azure OpenAI REST proxy
- Twilio (SMS Alert Services)
- Python-dotenv

### Deployment & Testing
- Render & Gunicorn
- Pytest (Complete in-process Flask test client integration suite)

## Fault Classes
1. Normal Operation
2. Overheating Fault
3. High Vibration Fault
4. Pressure Failure
5. Low Oil Level
6. Coolant Leakage Fault

## Dataset & AI Model Disclaimer
> [!NOTE]
> **Synthetic Dataset:** The dataset (`predictive_maintenance_dataset.csv`) used to train the machine learning classifier is generated synthetically (via `dataset_generator.py`) for modeling and demonstration purposes. It simulates realistic ranges, variations, and overlapping values of sensor telemetry (temperature, pressure, vibration, flow, oil level, and leakage) for different machine fault states. However, since the dataset is fully synthetic and not sourced from physical machinery, the classifier's accuracy and performance metrics are meant solely for demonstration and academic evaluation.

## Author
Oluwatobiloba Smithson