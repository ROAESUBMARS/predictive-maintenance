# NMU AI Predictive Maintenance Dashboard — Comprehensive Operating & User Manual

Welcome to the **Nigeria Maritime University (Marine Engineering) AI-Based Predictive Maintenance System User Manual**. This document provides an exhaustive, step-by-step operational guide for navigating, configuring, and utilizing all features across all user roles within the digital-twin dashboard.

---

## 1. System Architecture & Overview

The **NMU AI Predictive Maintenance System** is a state-of-the-art condition-based monitoring (CBM) and digital-twin platform engineered for heavy industrial machinery, specifically marine **Hydraulic Power Units (HPU-01)**.

### Core Capabilities
* **Machine Learning Fault Diagnosis:** Real-time multi-class fault classification using a trained RandomForest classifier.
* **LLM AI Copilot:** Interactive, streaming diagnostic advice powered by Gemini / OpenAI models with specialized domain personas.
* **Prescriptive Decision Matrix & RUL Engine:** Remaining Useful Life forecasting and actionable decision paths.
* **Decarbonization & Emissions Tracker:** IMO Carbon Intensity Indicator (CII) rating calculation, fuel waste cost modeling, and carbon tax fine estimations.
* **Predictive Spare Parts Procurement:** Automated spare parts inventory calculation with supplier lead-time warnings.
* **Role-Based Access Control (RBAC):** Customized viewports tailored for **Maintenance Technicians**, **Maintenance Engineers**, and **Reliability Engineers**.
* **Automated Safety Interlock:** Automatic emergency interlock tripping when equipment safety urgency drops below threshold.
* **Operational Technology (OT) Security:** Real-time sensor sanity checking, telemetry anti-tampering bounds, and threat metrics.

---

## 2. Authentication, RBAC & Global Interface Controls

### 2.1 Role-Based Access Control (RBAC) & Login
Upon accessing the application, you will encounter the **Role Selection Landing Screen**:

1. **Select Profile:**
   - 🔧 **Maintenance Technician:** Field-level view focused on executing assigned work orders, recording physical repairs, scanning QR codes, and shift handovers.
   - ⚙️ **Maintenance Engineer:** Diagnostic center featuring telemetry charts, root cause analysis, work order creation, procurement planning, decarbonization tracking, and AI Copilot interaction.
   - 📊 **Reliability Engineer:** Executive fleet management overview including 12-pump fleet health map, MTBF/MTTR analytics, ML model drift monitoring, Weibull distribution charts, and ERP audit package exports.

2. **Login Credentials & Roster:**
   - **Default Password:** `admin` (or configured via `API_PASSWORD` in `.env`).
   - **Technician Roster Emails:**
     - `sarah@nmu.edu.ng` (Sarah Jenkins)
     - `mike@nmu.edu.ng` (Mike Ross)
     - `david@nmu.edu.ng` (David Chen)
   - **Engineer Email:** `engineer@nmu.edu.ng` (or your registered administrative account)

> [!IMPORTANT]
> **Token Cryptography & API Security:** Authenticating issues a timed session token stored locally and attached as a Bearer token in the HTTP `Authorization` header for all backend calls (`/predict`, `/schedule`, `/recommend`, `/chat`, `/api/config`). Missing or invalid tokens return a `401 Unauthorized` HTTP code.

---

### 2.2 Global Topbar & Navigation Controls
Located at the top of the application shell:
* **Toggle Sidebar (`<i class="fa-solid fa-sliders"></i>`):** Expands or collapses the left-hand sensor control panel (Available in Technician and Engineer views).
* **API Server Endpoint Selector:** Input field allowing seamless connection switching between local server (e.g., `http://localhost:5001`) and remote cloud deployments.
* **Theme Selector Dropdown:**
  - **Dark Theme:** High-contrast dark modern glassmorphism (default).
  - **Daytime Theme:** Clean, bright daylight UI for outdoor field operations.
  - **High Contrast:** Accessibility-optimized high-visibility color scheme.
* **Switch Role Button (`↺ Switch Role`):** Logs out the current session token and returns to the main landing screen.

---

## 3. Sidebar: Sensor Controls & Simulation Engine

The expandable sidebar allows operators to simulate real-time machinery operational states and configure alert dispatching.

### 3.1 Presets & Manual Sensor Sliders
* **Scenario Presets:**
  - **Normal:** Standard baseline telemetry (Temp: ~70°C, Pressure: ~100 psi, Vib: ~0.02g, Flow: 300 lpm, Oil: 60%, RPM: 1500, Leak: No).
  - **Overheating:** Elevated temperature exceeding safe operating limit (> 88°C).
  - **High Vibration:** Excessive mechanical vibration (> 0.04g) indicating bearing wear or misalignment.
  - **Pressure Failure:** Hydraulic system pressure drop below minimum operational threshold (< 80 psi).
  - **Low Oil:** Engine oil level dangerously depleted (< 30%).
  - **Coolant Leak:** Active fluid leakage flagged in the cooling loop.
* **Manual Sliders:**
  - **Temperature:** 20°C to 150°C
  - **Pressure:** 0 psi to 200 psi
  - **Vibration:** 0.000g to 0.100g
  - **Flow Rate:** 0 lpm to 1000 lpm
  - **Oil Level:** 0% to 100%
  - **RPM:** 0 RPM to 5000 RPM
  - **Coolant Leak:** No (0) / Yes (1) toggle.

### 3.2 Alert Dispatch Settings
* **Recipient Email:** Email address (e.g., `profmariner01@gmail.com`) for automated SMTP alert dispatches upon critical diagnostic results.
* **Recipient Phone Number:** Phone number (e.g., `+2348030000000`) for Twilio SMS warning notifications.
* **Run Diagnostic Button (`⚡ Run Diagnostic`):** Executes backend feature normalization, ML inference, RUL calculation, decarbonization impact scoring, and schedule optimization.

---

## 4. Maintenance Technician Operating Guide

Optimized for mobile devices and field tablets used by on-site technicians.

```
+-----------------------------------------------------------------------+
| TECHNICIAN VIEW                                                      |
| +-------------------+ +---------------------------------------------+ |
| | FIELD ROSTER      | | WORK ORDER CONTAINER                        | |
| | - Sarah Jenkins   | | 🔒 Locked State (Scan QR Code required)     | |
| | - Mike Ross       | | 🔓 Unlocked State:                           | |
| | - David Chen      | |   • Active WO Details & Status Box          | |
| |                   | |   • Interactive Repair Checklist            | |
| |                   | |   • Required Spare Parts & Lead Times       | |
| |                   | |   • Field Actions (Ack, Photo, Voice, Complete)| |
| |                   | |   • Shift Handover Note Textarea            | |
| +-------------------+ +---------------------------------------------+ |
+-----------------------------------------------------------------------+
```

### 4.1 Roster Selection & Work Order Access
1. **Select Profile:** Click your name in the **Field Roster** on the left column.
2. **Work Order Selector:** Click on an assigned Work Order pill (e.g., `WO-8992`).

### 4.2 Asset QR Code Physical Verification
1. If the selected Work Order is **Locked**, the physical safety interlock requires location verification at the pump unit.
2. Click **Scan Asset QR Code**.
3. Use your device camera to scan the pump tag, or click **Simulate Scan to Open WO** for testing.
4. Upon successful scan, the Work Order unlocks immediately.

### 4.3 Actioning & Completing Work Orders
* **Review WO Details:** Inspect fault summary, target pump ID, and severity level.
* **Execute Repair Checklist:** Check off step-by-step physical procedures (e.g., *Isolate hydraulic line*, *Inspect O-ring seals*, *Refill fluid*).
* **Verify Spare Parts:** Check catalog numbers and quantities required.
* **Field Actions Panel:**
  - **Acknowledge Alert:** Marks ticket as actively being serviced in engineering logs.
  - **Upload Photo Proof:** Capture or attach repair photo evidence.
  - **Voice-to-Text Note:** Hands-free voice recording for maintenance commentary.
  - **Complete Work Order:** Triggers the interactive fulfillment modal with animated completion progress (`fulfilled`).
* **Shift Handover Note:** Type handover commentary for incoming technicians and click **Save Handover Note**.

---

## 5. Maintenance Engineer Operating Guide

The primary command hub for equipment diagnostics, maintenance scheduling, and decarbonization management.

### 5.1 Emergency Shutdown Interlock
* If sensor inputs trigger a severe condition where **Safety Urgency drops below 6/10**, the **AUTOMATIC EMERGENCY SHUTDOWN** interlock trips.
* A prominent red emergency banner activates with sound/visual warning.
* To restore operations after resolving the issue: Click **Reset Interlock & Restore Power**.

### 5.2 Key Metrics & Live Telemetry Streams
* **KPI Header Cards:** Live updates for *Health Index* (0-100), *Safety Urgency* (1-10), *Auto Interlock status*, *Remaining Useful Life (RUL)*, and *Cost Savings*.
* **Live Telemetry Stream Chart:** Dual-axis real-time chart tracking Temperature, Pressure, and Vibration history.
* **Raw Data Feed Table:** Tabular display of incoming sensor telemetry readings with timestamps.

### 5.3 Diagnostics, Root Cause & Decision Strategy Matrix
* **Active Diagnostic Card:** Shows current machine operational status (Nominal, Warning, Critical) with immediate prescriptive advice.
* **Fault Prediction Analysis:**
  - **AI Classification Probabilities:** Horizontal bar chart comparing probability percentages across all fault classes.
  - **Root Cause Feature Deviation (Z-Score):** Bar chart highlighting exactly which sensor metric deviates most from baseline standard deviation.
* **Decision Strategy Matrix Hub:**
  - **RUL Progress Gauge:** Visual meter showing estimated remaining operating hours (e.g., `720 hrs`).
  - **Prescriptive Decision Cards:** Multi-option operational strategies (e.g., *Option A: Immediate Shutdown*, *Option B: Derated Operating Mode*, *Option C: Continue Monitoring*).
  - **Root Cause Isolation:** Breakdown of root physical causes and cascading risk potentials.

### 5.4 Predictive Parts Procurement & Intelligent Scheduler
* **Suggested Procurement Panel (`#SWO-PROC-001`):**
  - Displays auto-generated spare parts list based on diagnosed fault.
  - **Lead-Time Warning Banner:** Alerts if supplier lead time exceeds remaining machinery operating hours.
  - **Part Details Table:** Catalog numbers, quantities, lead times (days), and estimated costs.
  - **Auto-Fill Work Order Button:** Transfers parts list and repair details directly into the Work Order Creation form.
* **Intelligent Maintenance Planner:** Recommends optimal servicing windows (e.g., *Scheduled within 24 hours*) to prevent catastrophic failure.

### 5.5 IMO Carbon Intensity & Decarbonization Tracker
* **IMO CII Rating Meter:** Calculates real-time carbon intensity performance grade (**Grade A** to **Grade E**).
* **Metrics Grid:**
  - **Actual Power Draw:** Real-time electrical power consumption vs nominal baseline.
  - **Fuel Waste Penalty:** Calculated financial loss rate ($/day and $/month) due to degraded efficiency.
  - **Excess CO₂ Emissions:** Extra carbon output (kg/day and annual tonnes).
  - **Carbon Tax Fine Estimation:** Projected regulatory financial penalty under EU ETS / IMO regulations (@ $95/tonne CO₂).
* **Decarbonization ROI Action Step:** Prescriptive guidance to restore Grade A efficiency.

### 5.6 Work Order Creation & Management
1. In the **Work Order Management** card:
   - **Assignee:** Select target technician (Sarah Jenkins, Mike Ross, David Chen).
   - **Priority:** Select *Critical (Immediate)*, *High (24hrs)*, or *Medium (7 days)*.
   - **Est. Repair Time:** Input target duration in Hours and Days.
2. Click **Generate Work Order** to post the work order into the active repairs tracking table and sync with the Technician view.

### 5.7 AI Copilot & Streaming Diagnostic Assistant
1. Locate the **AI Copilot** panel in the bottom right column.
2. Type any maintenance query (e.g., *"What is the standard procedure for replacing the main pump bearing on HPU-01?"*).
3. The Copilot outputs internal reasoning in `<thinking>` blocks followed by real-time streamed instruction paragraphs.
4. Toggle assistant specialist personas to tailor responses:
   - *Reliability Engineer*
   - *Maintenance Engineer*
   - *Mechanical Technician*
   - *Electrical Engineer*

---

## 6. Reliability Engineer Operating Guide

Designed for fleet reliability managers, asset integrity leads, and machine learning oversight.

### 6.1 Fleet KPIs & 12-Pump Fleet Health Map
* **Fleet KPIs:** *Fleet Health Score*, *Fleet MTBF (Mean Time Between Failures)*, *Fleet MTTR (Mean Time To Repair)*, and *False Alarm Rate*.
* **Fleet Health Map:** Grid representing 12 facility pump units (`HP-01` through `HP-12`). Color-coded indicators show real-time status:
  - 🟢 **Green:** Nominal operation.
  - 🟡 **Yellow:** Warning state requiring inspection.
  - 🔴 **Red:** Critical fault state requiring immediate intervention.

### 6.2 ML Model Performance Monitor & Drift Detection
* Displays real-time model metrics:
  - 30-Day Classification Accuracy (e.g., `98.4%`)
  - Precision and Recall by fault class
  - Feature Drift Flags (e.g., *Vibration sensor drift detected on Unit 7*)
  - Total Telemetry Samples processed since last retrain.
* **Trigger Model Retraining Button:** Click to execute an asynchronous automated retrain pipeline that refits the RandomForest classifier on recent telemetry data and validates performance before hot-swapping model weights.

### 6.3 Remaining Useful Life (RUL) Forecast & Weibull Analysis
* **Fleet RUL Forecast Table:** Tabular listing of estimated remaining operating cycles for watch-listed pump units.
* **Failure Distribution Analysis (Weibull Chart):** Interactive area chart plotting failure probability density over equipment operating cycles, helping pinpoint infant mortality vs wear-out phase.

### 6.4 Cost of Unreliability Analytics & Audit Exports
* **Financial Metrics:** Summarizes *Downtime Cost Avoided*, *Maintenance Cost Saved*, and overall *Payback Period*.
* **Export Buttons:**
  - 📄 **Export Reliability PDF:** Generates formal executive summary PDF report.
  - 📊 **Export Fleet Excel:** Downloads raw telemetry and fleet status datasheets.
  - 🔍 **Generate RCFA Report:** Generates Root Cause Failure Analysis documentation.
  - 📐 **Benchmark vs ISO 14224:** Produces ISO 14224-compliant failure mode audit packages for enterprise ERP systems (**SAP PM**, **AMOS**) and Classification Societies (**DNV**, **Lloyd's Register**, **ABS**).

---

## 7. Step-by-Step Operational Workflows & Simulations

### Scenario A: Simulating & Resolving an Overheating Fault
1. **Trigger Overheating State:**
   - Open the left sidebar.
   - Set **Preset Scenario** to `Overheating` (or slide **Temperature** slider to `95°C`).
   - Click **Run Diagnostic**.
2. **Observe Engineer View Updates:**
   - Emergency interlock check evaluates condition.
   - Diagnostic panel displays `OVERHEATING FAULT DETECTED`.
   - Z-score deviation chart spikes on Temperature.
   - Suggested Procurement updates required cooling lines / seal replacements.
   - IMO CII rating drops to **Grade D** due to thermal inefficiency; fuel waste penalties rise.
3. **Dispatch & Action Work Order:**
   - In Work Order Management, click **Generate Work Order** assigned to **Sarah Jenkins**.
   - Switch role to **Maintenance Technician**.
   - Select **Sarah Jenkins** in Field Roster.
   - Click **Scan Asset QR Code** -> **Simulate Scan to Open WO**.
   - Complete repair checklist items.
   - Click **Complete Work Order** to finalize.

---

## 8. Server Setup, API Commands & Troubleshooting

### 8.1 Starting the Application Server
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies if needed
pip install -r requirements.txt

# Launch Flask development application
python app.py
```
Server starts on `http://127.0.0.1:5001`. Open `http://localhost:5001` or `index.html` in your web browser.

### 8.2 Common Error Codes & Troubleshooting
* **`401 Unauthorized`:** Session token has expired or is invalid. Click **↺ Switch Role** and re-authenticate using password `admin`.
* **Telemetry Streaming:** System streams telemetry via Server-Sent Events (SSE) and falls back gracefully to 1s REST API polling.
* **Model Retraining Warning:** If feature drift warning persists, click **Trigger Model Retraining** in Reliability view.

---
*NMU AI Predictive Maintenance Project — Dept of Marine Engineering (U2021/MAE/278)*

