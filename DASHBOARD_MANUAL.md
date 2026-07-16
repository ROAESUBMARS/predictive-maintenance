# NMU AI Predictive Maintenance Dashboard — User Manual

Welcome to the Nigeria Maritime University (Marine Engineering) **AI-Based Predictive Maintenance Dashboard User Manual**. This guide provides step-by-step instructions on how to access, configure, and utilize the dashboard's features for each industrial maintenance role.

---

## 1. Authentication & Access

Upon loading the application, you will be presented with the **Role Authentication Screen**.

1. **Select a Role:** Choose from the three available profiles:
   - **Maintenance Technician** (On-site repairs)
   - **Maintenance Engineer** (Planning, diagnostics, and coordination)
   - **Reliability Engineer** (Fleet analytics and ML model oversight)
2. **Log In:** Click **Enter as [Role]** to open the login modal.
3. **Credentials:** 
   - **Default Password:** `admin` (or configured via the `API_PASSWORD` environment variable on the server).
   - **Technician Emails:** `sarah@nmu.edu.ng`, `mike@nmu.edu.ng`, or `david@nmu.edu.ng`
   - **Engineer Email:** `engineer@nmu.edu.ng` (or your registered admin email)

> [!IMPORTANT]
> **Backend-Level API Security & Token Verification:** Unlike typical static frontend apps, all primary API backend endpoints (including `/predict`, `/schedule`, `/recommend`, `/chat`, and `/api/config`) are protected by a server-side authentication hook. The password entered at login is securely kept as a session token on the client and appended as a Bearer token in the `Authorization` header of all requests. Invalid or missing headers result in a `401 Unauthorized` response.

---

## 2. Sensor Adjustments & Sidebar Controls
*(Available to Technicians and Engineers)*

The sidebar provides controls to simulate and analyze various equipment states.

* **Scenario Presets:** Select from the dropdown menu to instantly configure the sensors:
  - **Normal:** Baseline operational telemetry.
  - **Overheating:** Temperature elevated above warning levels (> 88°C).
  - **High Vibration:** Vibration readings exceeding standard limits (> 0.04g).
  - **Pressure Failure:** Hydraulic or line pressure dropped below standard values (< 80 psi).
  - **Low Oil:** Engine oil level depleted (< 30%).
  - **Coolant Leak:** Active coolant leak state active.
* **Manual Sliders:** Use sliders to manually adjust **Temperature**, **Pressure**, **Vibration**, **Flow Rate**, **Oil Level**, and **RPM**.
* **Alert Dispatch Settings:**
  - Enter the recipient's **Email Address** and **Phone Number** in the sidebar.
  - Automated warnings will be dispatched via SMTP/Twilio when severe faults are diagnosed.
* **Run Diagnostic:** Click the **Run Diagnostic** button to run the predictive analysis using the active ML model (or rule-based fallback).

---

## 3. Maintenance Technician View

This dashboard is optimized for field-level maintenance personnel.

### 3.1 Unlocking Work Orders
1. Select your technician name from the **Field Roster** on the left.
2. Click on an assigned Work Order (e.g., `WO-8992`).
3. If the Work Order is **Locked**, you must verify your physical presence at the pump:
   - Click **Scan Asset QR Code** to bring up the camera scanner.
   - Click **Simulate Scan to Open WO** to mock the physical presence check.

### 3.2 Actioning the Work Order
* **Repair Checklist:** Check off the physical maintenance tasks as you execute them.
* **Required Spare Parts:** Review and verify the usage of necessary parts.
* **Field Actions:**
  - **Acknowledge Alert:** Confirm you are working on the fault.
  - **Upload Photo Proof:** Log evidence of the completed repair.
  - **Voice-to-Text Note:** Record maintenance logs hands-free.
  - **Complete Work Order:** Submit the ticket for engineering review.
* **Shift Handover:** Leave quick handover notes at the bottom for the incoming shift.

---

## 4. Maintenance Engineer View

The central dashboard for system diagnostics, scheduling, and engineering oversight.

### 4.1 Live Telemetry & Active Diagnostics
* **Live Telemetry Stream:** A live chart displays historical trends for sensor inputs.
* **Raw Data Feed:** View the tabular log of incoming telemetry metrics.
* **Active Diagnostics Panel:** Shows the ML predicted fault name, severity (OK, Warning, Critical), and immediate advice.
* **Fault Prediction Analysis:**
  - **AI Classification Probabilities:** Displays confidence levels for each fault class.
  - **Root Cause Feature Deviation:** Shows the Z-score deviation chart to pinpoint which sensor triggered the anomaly.

### 4.2 Work Order Management
*(Located below the Raw Data Feed)*
* **Create New Work Orders:**
  - Assign tasks to technicians (Sarah, Mike, David).
  - Choose task priority (Critical, High, Medium).
  - Set estimated repair time (Hours and Days).
  - Click **Generate Work Order** to add it to the active repair log.
* **Active Repairs Tracker:** Monitor all active work order statuses and logged durations.

### 4.3 AI Copilot & Streaming Chat
* **Engage the AI:** Type questions in the **AI Copilot** prompt area to receive maintenance, assembly, or safety instructions.
* **Specialist Personas:** Toggle settings to switch between *Reliability Engineer*, *Maintenance Engineer*, *Mechanical Technician*, and *Electrical Engineer* personas.
* **Streamed Responses:** The AI assistant displays its internal reasoning in `<thinking>` blocks followed by streamed response paragraphs.

---

## 5. Reliability Engineer View

A strategy-level dashboard for asset life-cycle evaluation and ML validation.

* **Fleet Metrics:** Monitor overall health scores, Fleet MTBF (Mean Time Between Failures), Fleet MTTR (Mean Time To Repair), and False Alarm rates.
* **Fleet Health Map:** A visual map indicating the operational status of all 12 pumps across the facility.
* **ML Model Monitor:** View the active accuracy score and precision/recall stats. If drift is detected, click **Trigger Model Retraining** to retrain the underlying ML model.
* **Remaining Useful Life (RUL) Forecast:** Review future projections for pump failures (e.g., cycles remaining) to plan capital replacements.
* **Weibull Distribution:** Analyze failure probabilities plotted over cycles on the Failure Distribution area chart.
* **Reports Export:** Export data sheets, PDF reports, or generate ISO 14224 benchmarking audits.
