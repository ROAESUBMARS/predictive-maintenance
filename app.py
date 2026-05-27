from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.environ.get("MODEL_PATH", "saved_model.pkl")
model = None

try:
    model = joblib.load(MODEL_PATH)
    print(f"[OK] Model loaded from {MODEL_PATH}")
except Exception as e:
    print(f"[!] Model not found ({e}). Using rule-based fallback.")

FAULT_INFO = {
    0: {"fault": "System Operating Normally",   "recommendation": "No maintenance required. All parameters within normal range.", "severity": "ok"},
    1: {"fault": "Overheating Fault",            "recommendation": "Check cooling system and inspect pump bearings.", "severity": "critical"},
    2: {"fault": "High Vibration Fault",         "recommendation": "Inspect rotating parts and tighten loose components.", "severity": "critical"},
    3: {"fault": "Pressure Failure",             "recommendation": "Check hydraulic pressure lines and pump condition.", "severity": "critical"},
    4: {"fault": "Low Oil Level",                "recommendation": "Refill oil and inspect for leakage.", "severity": "warning"},
    5: {"fault": "Coolant Leakage Fault",        "recommendation": "Inspect coolant pipes and repair leakage.", "severity": "critical"},
}

FEATURE_COLS = [
    "Temperature_C", "Pressure_psi", "Vibration_g",
    "Flow_Rate_lpm", "Oil_Level_pct", "RPM", "Coolant_Leak",
    "Operating_Hours"
]

def rule_based_classify(d):
    if d.get("Coolant_Leak", 0) == 1:
        return 5
    if d.get("Oil_Level_pct", 100) < 30:
        return 4
    if d.get("Pressure_psi", 100) < 80:
        return 3
    if d.get("Vibration_g", 0) > 0.04:
        return 2
    if d.get("Temperature_C", 70) > 88:
        return 1
    return 0


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "mode": "ml_model" if model else "rule_based"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    try:
        payload = {
            "Temperature_C":   float(data.get("Temperature_C", 0)),
            "Pressure_psi":    float(data.get("Pressure_psi", 0)),
            "Vibration_g":     float(data.get("Vibration_g", 0)),
            "Flow_Rate_lpm":   float(data.get("Flow_Rate_lpm", 0)),
            "Oil_Level_pct":   float(data.get("Oil_Level_pct", 0)),
            "RPM":             float(data.get("RPM", 0)),
            "Coolant_Leak":    int(data.get("Coolant_Leak", 0)),
            "Operating_Hours": float(data.get("Operating_Hours", 100)),
        }

        if model is not None:
            df = pd.DataFrame([payload])[FEATURE_COLS]
            prediction = int(model.predict(df)[0])
        else:
            prediction = rule_based_classify(payload)

        result = FAULT_INFO[prediction]
        return jsonify({
            "fault_code": prediction,
            "fault": result["fault"],
            "recommendation": result["recommendation"],
            "severity": result["severity"],
            "mode": "ml_model" if model else "rule_based",
            "inputs": payload
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)