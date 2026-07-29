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

## Commercial Market Positioning & Multi-Tenant Fleet-as-a-Service (FaaS) SaaS Architecture
> [!IMPORTANT]
> **Market Structure & Business Model:**
> The global commercial digital-twin and marine predictive maintenance market is structurally divided into three core verticals: **Hardware** (IoT telemetry sensors, edge gateways, satellite communications), **Software** (predictive diagnostics, Remaining Useful Life [RUL] forecasting, decarbonization analytics), and **Services** (managed fleet monitoring, remote technical support). Predictive maintenance serves as the leading software application within this ecosystem.
> 
> While single-vessel monitoring provides immediate operational utility, the true commercial leverage of this architecture stems from scaling the **Reliability Engineer Fleet View** into a multi-tenant **Fleet-as-a-Service (FaaS) SaaS Platform**:
> - **Multi-Client Tenant Isolation**: Independent shipping lines and fleet operators log into segregated organization workspaces to manage their respective vessel assets and machinery telemetry.
> - **Subscription Monetization**: Tiered monthly/annual recurring revenue (ARR) model priced per monitored vessel or auxiliary machinery asset (e.g. $150–$300/asset/month).
> - **Compliance & Financial ROI**: Integrates maintenance scheduling with regulatory frameworks like the IMO Carbon Intensity Indicator (CII) and EU Emissions Trading System (EU ETS), elevating the platform from an operational maintenance tool into an executive-level financial risk and decarbonization asset.
- **Enterprise ERP & Class Society Integration Hooks**: Exposes standard API data export interfaces (JSON/ISO 14224 structured formats) designed for seamless integration with Maritime Planned Maintenance Systems (PMS) and Enterprise Resource Planning (ERP) tools like **SAP PM**, **AMOS**, and **AMOPS**, as well as digital audit data packages tailored for Classification Society compliance verifications (**DNV**, **Lloyd's Register**, **American Bureau of Shipping [ABS]**, and **Bureau Veritas [BV]**).
- **Cybersecurity & OT Telemetry Anomaly Monitoring Layer**: Implements an operational technology (OT) data pipeline security module (`ot_security.py`) that monitors physical sensor plausibility bounds to detect sensor tampering/spoofing, mitigates Industry 4.0 man-in-the-middle risks, tracks unauthorized access bursts, and exposes live threat-level metrics via `/api/ot-security/status`.

## Dataset & AI Model Disclaimer
> [!NOTE]
> **Synthetic Dataset:** The dataset (`predictive_maintenance_dataset.csv`) used to train the machine learning classifier is generated synthetically (via `dataset_generator.py`) for modeling and demonstration purposes. It simulates realistic ranges, variations, and overlapping values of sensor telemetry (temperature, pressure, vibration, flow, oil level, and leakage) for different machine fault states. However, since the dataset is fully synthetic and not sourced from physical machinery, the classifier's accuracy and performance metrics are meant solely for demonstration and academic evaluation.

## Author
Oluwatobiloba Smithson