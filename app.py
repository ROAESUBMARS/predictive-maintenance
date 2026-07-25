from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import joblib
import pandas as pd
import os
import logging
import time
from collections import defaultdict
from dotenv import load_dotenv
import secrets

# Load environment variables on startup
load_dotenv()

# Configure standard python logging for production environments (like Render)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from ai_recommendation import AIRecommendationEngine
from alert_service import trigger_fault_alerts
from maintenance_scheduler import MaintenanceScheduler

app = Flask(__name__)

# Configure serializer for timed cryptographically-signed tokens
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
if not SECRET_KEY:
    is_prod = os.environ.get("VERCEL") or os.environ.get("RENDER") or os.environ.get("ENV") == "production" or os.environ.get("FLASK_ENV") == "production"
    if is_prod:
        raise RuntimeError(
            "FATAL: FLASK_SECRET_KEY environment variable is not set! "
            "In production environments (like Vercel or Render), you must set a persistent "
            "FLASK_SECRET_KEY to prevent session tokens from becoming invalid randomly due to cold starts or multiple worker processes."
        )
    else:
        logger.warning(
            "\n"
            "========================================================================\n"
            "⚠️ WARNING: FLASK_SECRET_KEY environment variable is not set!\n"
            "Generating a temporary ephemeral key for local development.\n"
            "Note: Sessions will be invalidated whenever the server restarts.\n"
            "To resolve this, set FLASK_SECRET_KEY in your .env file or environment.\n"
            "========================================================================\n"
        )
        SECRET_KEY = secrets.token_hex(32)
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Warn if running with default API password in non-debug context
api_password = os.environ.get("API_PASSWORD", "admin")
debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() in ["true", "1"]
if api_password == "admin" and not debug_mode:
    logger.warning(
        "\n"
        "========================================================================\n"
        "⚠️ SECURITY WARNING: Using the default API password ('admin')!\n"
        "It is highly recommended to change this by setting the API_PASSWORD\n"
        "environment variable to prevent unauthorized access.\n"
        "========================================================================\n"
    )

# Simple user database mapping emails to their registered role
USER_DATABASE = {
    "sarah@nmu.edu.ng": "tech",
    "mike@nmu.edu.ng": "tech",
    "david@nmu.edu.ng": "tech",
    "tech@nmu.edu.ng": "tech",
    "eng@nmu.edu.ng": "eng",
    "rel@nmu.edu.ng": "rel",
}

# Configure CORS to restrict allowed origins (defaults to local development urls)
allowed_origins_env = os.environ.get("ALLOWED_CORS_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000,http://localhost:5001,http://127.0.0.1:5001")
allowed_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
CORS(app, resources={r"/*": {"origins": allowed_origins}})

def require_roles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role = getattr(g, "current_role", None)
            if not role or role not in roles:
                return jsonify({"error": "Forbidden: Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

_rate_limit_records = defaultdict(list)

def rate_limit(limit=10, period=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Developer bypass to prevent test suite lockouts
            if getattr(g, "current_user", None) == "developer":
                return f(*args, **kwargs)

            client_id = getattr(g, "current_user", None) or request.remote_addr
            key = f"{client_id}:{request.path}"
            
            now = time.time()
            _rate_limit_records[key] = [t for t in _rate_limit_records[key] if now - t < period]
            
            if len(_rate_limit_records[key]) >= limit:
                return jsonify({
                    "error": "Too Many Requests: Rate limit exceeded. Please try again later.",
                    "retry_after": int(period - (now - _rate_limit_records[key][0]))
                }), 429
                
            _rate_limit_records[key].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.before_request
def check_auth():
    # Allow CORS preflight requests
    if request.method == "OPTIONS":
        return None
        
    # Allow public access to home, health, login, static files
    if request.path in ["/", "/health", "/api/login"] or request.path.startswith("/static/"):
        return None
        
    auth_header = request.headers.get("Authorization")
    api_key = request.headers.get("X-API-Key")
    admin_key = request.headers.get("X-Admin-Key")
    
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    elif api_key:
        token = api_key
    elif admin_key:
        token = admin_key
        
    if not token:
        return jsonify({"error": "Unauthorized: Missing authentication token"}), 401

    # Expected API password (default to admin)
    expected_password = os.environ.get("API_PASSWORD", "admin")

    # Developer/test direct key fallback (only if DEV_BYPASS_TOKEN is set in environment)
    dev_bypass_token = os.environ.get("DEV_BYPASS_TOKEN")
    if dev_bypass_token and secrets.compare_digest(token, dev_bypass_token):
        g.current_user = "developer"
        g.current_role = "eng"
        return None

    # Verify cryptographic session token
    try:
        data = serializer.loads(token, max_age=86400)  # Valid for 24 hours
        g.current_user = data.get("email")
        g.current_role = data.get("role")
    except (SignatureExpired, BadSignature):
        return jsonify({"error": "Unauthorized: Invalid or expired session token"}), 401


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    requested_role = data.get("role", "").strip().lower()

    if not email or not password or not requested_role:
        return jsonify({"error": "Missing email, password, or role"}), 400

    expected_password = os.environ.get("API_PASSWORD", "admin")
    if not secrets.compare_digest(password, expected_password):
        return jsonify({"error": "Invalid password"}), 401

    if email not in USER_DATABASE:
        return jsonify({"error": "User email not authorized"}), 401

    registered_role = USER_DATABASE[email]
    if registered_role != requested_role:
        return jsonify({"error": f"Role mismatch. Registered as {registered_role}"}), 403

    # Generate a timed, signed token
    token = serializer.dumps({"email": email, "role": registered_role})
    return jsonify({
        "status": "success",
        "token": token,
        "role": registered_role,
        "email": email
    })


@app.route("/", methods=["GET"])
def home():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, "index.html")

MODEL_PATH = os.environ.get("MODEL_PATH", "saved_model.pkl")
model = None

try:
    model = joblib.load(MODEL_PATH)
    logger.info(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    logger.warning(f"Model not found ({e}). Using rule-based fallback.")

# Instantiate the AI recommendation engine once at startup
rec_engine = AIRecommendationEngine()
logger.info("AIRecommendationEngine ready.")

# Instantiate the Maintenance Scheduler once at startup
scheduler = MaintenanceScheduler()
logger.info("MaintenanceScheduler ready.")

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


def _parse_sensor_payload(data: dict) -> dict:
    """Validate and normalise incoming sensor JSON into a clean payload dict."""
    return {
        "Temperature_C":   float(data.get("Temperature_C", 0)),
        "Pressure_psi":    float(data.get("Pressure_psi", 0)),
        "Vibration_g":     float(data.get("Vibration_g", 0)),
        "Flow_Rate_lpm":   float(data.get("Flow_Rate_lpm", 0)),
        "Oil_Level_pct":   float(data.get("Oil_Level_pct", 0)),
        "RPM":             float(data.get("RPM", 0)),
        "Coolant_Leak":    int(data.get("Coolant_Leak", 0)),
        "Operating_Hours": float(data.get("Operating_Hours", 100)),
    }


def _payload_to_dataframe(payload: dict) -> pd.DataFrame:
    """Convert parsed sensor payload dict into a DataFrame matching model feature columns."""
    model_features = [c for c in FEATURE_COLS if c != "Operating_Hours"]
    return pd.DataFrame([payload])[model_features]


def _run_prediction(payload: dict):
    """Run ML model (or fallback) and return (fault_code, confidence, mode)."""
    if model is not None:
        df = _payload_to_dataframe(payload)
        fault_code = int(model.predict(df)[0])
        try:
            proba = model.predict_proba(df)[0]
            confidence = float(proba[fault_code])
        except AttributeError:
            confidence = 0.87
        mode = "ml_model"
    else:
        fault_code = rule_based_classify(payload)
        confidence = 0.85
        mode = "rule_based"
    return fault_code, confidence, mode


def _get_feature_contributions(payload):
    # Normal baselines: (mean, std)
    baselines = {
        "Temperature_C": (70.0, 15.0),
        "Pressure_psi": (100.0, 15.0),
        "Vibration_g": (0.02, 0.015),
        "Flow_Rate_lpm": (300.0, 50.0),
        "Oil_Level_pct": (60.0, 15.0),
        "RPM": (1500.0, 300.0),
    }
    contributions = {}
    for col, (mean, std) in baselines.items():
        val = payload.get(col, mean)
        z = abs(val - mean) / std
        contributions[col] = round(z, 2)
    contributions["Coolant_Leak"] = 3.0 if payload.get("Coolant_Leak", 0) == 1 else 0.0
    return contributions


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "mode": "ml_model" if model else "rule_based",
        "recommendation_engine": "AIRecommendationEngine v1.0"
    })


@app.route("/predict", methods=["POST"])
@rate_limit(limit=120, period=60)  # Raised to support live telemetry (every 2s = 30 req/min)
def predict():
    """
    Predict fault from sensor data.

    Returns the original compact response PLUS the full AI recommendation
    block for backwards-compatibility with older clients.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    try:
        payload = _parse_sensor_payload(data)
        fault_code, confidence, mode = _run_prediction(payload)

        result = FAULT_INFO[fault_code]

        # ── AI Recommendation Engine ──────────────────────────────
        rec = rec_engine.generate_recommendations(fault_code, payload, confidence)

        # Trigger alerts if configured and severity requires it
        alert_email = data.get("alert_email")
        alert_phone = data.get("alert_phone")
        if (alert_email or alert_phone) and getattr(g, "current_user", None) != "developer":
            logged_in_email = getattr(g, "current_user", None)
            if not alert_email or not logged_in_email or alert_email.strip().lower() != logged_in_email.lower():
                return jsonify({"error": "Forbidden: You can only trigger alerts to your own registered email address."}), 403

        if alert_email or alert_phone:
            if rec["severity"] in ["warning", "critical"]:
                trigger_fault_alerts(
                    fault_name=rec["fault_name"],
                    severity=rec["severity"],
                    recommendations="\n".join(rec["primary_actions"]),
                    to_email=alert_email,
                    to_phone=alert_phone
                )

        # Extract class probabilities if available
        if model is not None:
            try:
                df = _payload_to_dataframe(payload)
                proba = model.predict_proba(df)[0].tolist()
            except Exception:
                proba = [0.0] * 6
                proba[fault_code] = confidence
        else:
            proba = [0.02] * 6
            proba[fault_code] = confidence

        contributions = _get_feature_contributions(payload)

        return jsonify({
            # Original fields (backwards-compatible)
            "fault_code":      fault_code,
            "fault":           result["fault"],
            "recommendation":  result["recommendation"],
            "severity":        result["severity"],
            "mode":            mode,
            "inputs":          payload,
            "probabilities":   proba,
            "feature_contributions": contributions,
            # Rich AI recommendation fields
            "ai_recommendation": {
                "fault_name":         rec["fault_name"],
                "confidence":         rec["confidence"],
                "confidence_rating":  rec["confidence_rating"],
                "risk_level":         rec["risk_level"],
                "urgency_level":      rec["urgency_level"],
                "primary_actions":    rec["primary_actions"],
                "preventive_measures": rec["preventive_measures"],
                "estimated_downtime": rec["estimated_downtime"],
                "sensor_health":      rec["sensor_health"],
                "anomalies":          rec["anomalies"],
                "spare_parts":        rec["spare_parts"],
                "cost_estimate":      rec["cost_estimate"],
                "next_check":         rec["next_check"],
                "technician_notes":   rec["technician_notes"],
                "rul_info":           rec.get("rul_info", {}),
                "decision_matrix":   rec.get("decision_matrix", []),
                "cascading_risks":   rec.get("cascading_risks", []),
                "root_causes":        rec.get("root_causes", []),
                "urgency_score_info": rec.get("urgency_score_info", {}),
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/schedule", methods=["POST"])
@rate_limit(limit=120, period=60)
def schedule():
    """
    Intelligent maintenance scheduling endpoint.
    Accepts fault_code, confidence, and operating_hours,
    and returns optimized scheduling details.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    try:
        fault_code = int(data.get("fault_code", 0))
        confidence = float(data.get("confidence", 1.0))
        operating_hours = float(data.get("operating_hours", 100))

        result = scheduler.schedule_next_maintenance(
            fault_code=fault_code,
            confidence=confidence,
            operating_hours=operating_hours
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recommend", methods=["POST"])
@rate_limit(limit=30, period=60)
def recommend():
    """
    Standalone AI recommendation endpoint.
    Accepts sensor data JSON, runs prediction + AIRecommendationEngine,
    and returns the full structured recommendation object.

    This is the endpoint consumed by index.html after a client-side diagnosis.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    try:
        payload = _parse_sensor_payload(data)

        # Accept an explicit fault_code override (from the JS classify()),
        # or re-run model/rule-based if not provided.
        if "fault_code" in data:
            fault_code = int(data["fault_code"])
            confidence = float(data.get("confidence", 0.85))
        else:
            fault_code, confidence, _ = _run_prediction(payload)

        rec = rec_engine.generate_recommendations(fault_code, payload, confidence)

        # Trigger alerts if configured and severity requires it
        alert_email = data.get("alert_email")
        alert_phone = data.get("alert_phone")
        if (alert_email or alert_phone) and getattr(g, "current_user", None) != "developer":
            logged_in_email = getattr(g, "current_user", None)
            if not alert_email or not logged_in_email or alert_email.strip().lower() != logged_in_email.lower():
                return jsonify({"error": "Forbidden: You can only trigger alerts to your own registered email address."}), 403

        if alert_email or alert_phone:
            if rec["severity"] in ["warning", "critical"]:
                trigger_fault_alerts(
                    fault_name=rec["fault_name"],
                    severity=rec["severity"],
                    recommendations="\n".join(rec["primary_actions"]),
                    to_email=alert_email,
                    to_phone=alert_phone
                )

        return jsonify({
            "fault_code":          rec["fault_code"],
            "fault_name":          rec["fault_name"],
            "severity":            rec["severity"],
            "confidence":          rec["confidence"],
            "confidence_rating":   rec["confidence_rating"],
            "risk_level":          rec["risk_level"],
            "urgency_level":       rec["urgency_level"],
            "primary_actions":     rec["primary_actions"],
            "preventive_measures": rec["preventive_measures"],
            "estimated_downtime":  rec.get("estimated_downtime", "N/A"),
            "sensor_health":       rec["sensor_health"],
            "anomalies":          rec["anomalies"],
            "spare_parts":        rec["spare_parts"],
            "cost_estimate":      rec["cost_estimate"],
            "next_check":         rec["next_check"],
            "technician_notes":    rec["technician_notes"],
            "rul_info":           rec.get("rul_info", {}),
            "decision_matrix":   rec.get("decision_matrix", []),
            "cascading_risks":   rec.get("cascading_risks", []),
            "root_causes":        rec.get("root_causes", []),
            "urgency_score_info": rec.get("urgency_score_info", {}),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


SENSITIVE_KEYS = [
    "SMTP_PASS", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", 
    "GEMINI_API_KEY", "AZURE_OPENAI_API_KEY", "NVIDIA_API_KEY"
]

NON_SENSITIVE_KEYS = [
    "SMTP_SERVER", "SMTP_PORT", "SMTP_USER", "SMTP_FROM",
    "TWILIO_FROM_NUMBER", "GEMINI_MODEL",
    "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME", "AZURE_OPENAI_API_VERSION"
]

def mask_key(val):
    if not val:
        return ""
    n = len(val)
    if n <= 8:
        return "******"
    if n <= 16:
        return f"{val[:2]}...{val[-2:]}"
    return f"{val[:4]}...{val[-4:]}"


@app.route("/api/config", methods=["GET"])
@require_roles("eng", "rel")
def get_config():
    """Return active configurations, exposing only non-sensitive variables and masked sensitive variables."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except Exception:
        pass

    config_data = {}
    for k in NON_SENSITIVE_KEYS:
        config_data[k] = os.environ.get(k, "")
        
    for k in SENSITIVE_KEYS:
        val = os.environ.get(k, "")
        config_data[k] = mask_key(val)
        config_data[f"{k}_CONFIGURED"] = bool(val)
            
    return jsonify(config_data)


@app.route("/api/config", methods=["POST"])
@require_roles("eng", "rel")
def update_config():
    """Update non-sensitive environment variables and persist them. Keys must be set server-side."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    lines = []
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()

    current_config = {}
    for line in lines:
        line_s = line.strip()
        if line_s and not line_s.startswith("#") and "=" in line_s:
            k, v = line_s.split("=", 1)
            current_config[k.strip()] = v.strip().strip('"').strip("'")

    updated_any = False
    for k in NON_SENSITIVE_KEYS:
        if k in data:
            val = data[k].strip()
            if val and ("..." in val or val == "******"):
                continue
            current_config[k] = val
            os.environ[k] = val
            updated_any = True

    # Log security warnings if client tried to submit provider keys
    for k in SENSITIVE_KEYS:
        if k in data:
            logger.warning(f"Client tried to submit provider key '{k}' via API. Request ignored.")

    if updated_any:
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write("# Persistent configuration saved via Dashboard Backend Setup\n")
                for k, v in current_config.items():
                    f.write(f'{k}="{v}"\n')
        except (IOError, OSError) as e:
            logger.error(f"Failed to write configuration to .env: {str(e)}")
            return jsonify({
                "error": "Configuration could not be saved because the server's file system is read-only or ephemeral. "
                         "Please configure environment variables directly in your hosting platform's settings dashboard (Render/Vercel)."
            }), 400
        
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)
        except Exception:
            pass

    return jsonify({
        "status": "success", 
        "message": "Configuration updated successfully. Provider API keys are protected and must be managed server-side."
    })



@app.route("/chat", methods=["POST"])
@rate_limit(limit=30, period=60)
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    # Security enforcement: Do not allow client to send or override API keys in the request body
    if "gemini_api_key" in data or "nvidia_api_key" in data or ("azure_config" in data and isinstance(data["azure_config"], dict) and "api_key" in data["azure_config"]):
        return jsonify({"error": "Bad Request: Provider API keys must be configured server-side"}), 400

    messages = data.get("messages", [])
    sensor_data = data.get("sensor_data", {})
    diagnosis = data.get("diagnosis", {})
    persona = data.get("persona", "Maintenance Engineer")
    
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except Exception:
        pass

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        gemini_key = gemini_key.strip()
        if "placeholder" in gemini_key.lower() or "your_" in gemini_key.lower() or len(gemini_key) < 10:
            gemini_key = None

    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    if nvidia_key:
        nvidia_key = nvidia_key.strip()
        if "placeholder" in nvidia_key.lower() or "your_" in nvidia_key.lower() or len(nvidia_key) < 10:
            nvidia_key = None

    # NVIDIA_MODEL takes precedence; falls back to GEMINI_MODEL for backwards compatibility
    nvidia_model = os.environ.get("NVIDIA_MODEL") or os.environ.get("GEMINI_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")

    azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
    if azure_key:
        azure_key = azure_key.strip()
        if "placeholder" in azure_key.lower() or "your_" in azure_key.lower() or len(azure_key) < 10:
            azure_key = None
            
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    base_prompt = (
        "You are an expert industrial maintenance AI assistant. You help users diagnose and troubleshoot "
        "industrial equipment based on real-time sensor metrics and fault predictions.\n\n"
    )
    
    if persona == "Reliability Engineer":
        base_prompt += "Your primary focus is on MTBF (Mean Time Between Failures), long-term asset life-cycle, predictive degradation trends, statistical root-cause analysis, and systematic reliability improvement.\n\n"
    elif persona == "Maintenance Engineer":
        base_prompt += "Your primary focus is on workflow scheduling, prescriptive maintenance planning, risk mitigation, and spare parts management. Provide actionable plans to resolve the issue efficiently.\n\n"
    elif persona == "Mechanical Technician":
        base_prompt += "Your primary focus is on providing highly actionable, step-by-step physical repair procedures, safety protocols, required hand-tools, torque specifications, and mechanical assembly instructions.\n\n"
    elif persona == "Electrical Engineer":
        base_prompt += "Your primary focus is on sensor health, PLC integrations, voltage/current draw anomalies, wiring integrity, signal noise, and motor electrical diagnostics.\n\n"
    
    system_prompt = base_prompt
    if sensor_data:
        system_prompt += (
            "Current Sensor Telemetry:\n"
            f"- Temperature: {sensor_data.get('Temperature_C', 'N/A')} °C\n"
            f"- Pressure: {sensor_data.get('Pressure_psi', 'N/A')} psi\n"
            f"- Vibration: {sensor_data.get('Vibration_g', 'N/A')} g\n"
            f"- Flow Rate: {sensor_data.get('Flow_Rate_lpm', 'N/A')} LPM\n"
            f"- Oil Level: {sensor_data.get('Oil_Level_pct', 'N/A')}%\n"
            f"- RPM: {sensor_data.get('RPM', 'N/A')}\n"
            f"- Coolant Leak: {'Yes' if sensor_data.get('Coolant_Leak') == 1 else 'No'}\n"
            f"- Operating Hours: {sensor_data.get('Operating_Hours', 'N/A')} hours\n\n"
        )

    if diagnosis:
        system_prompt += (
            "Active Diagnostics & Decision Matrix:\n"
            f"- Predicted Fault: {diagnosis.get('fault_name', 'N/A')} (Code: {diagnosis.get('fault_code', 'N/A')})\n"
            f"- Recommended Action: {diagnosis.get('recommendation', 'N/A')}\n"
            f"- Severity: {diagnosis.get('severity', 'N/A').upper()}\n"
            f"- Remaining Useful Life (RUL): {diagnosis.get('rul_info', {}).get('rul_hours', 'N/A')} hours ({diagnosis.get('rul_info', {}).get('confidence_range', '')})\n"
        )
        if diagnosis.get('decision_matrix'):
            system_prompt += "- Prescriptive Decision Options:\n"
            for opt in diagnosis.get('decision_matrix'):
                system_prompt += f"  • {opt.get('title')} [{opt.get('tag')}]: Risk {opt.get('risk_score')}%, Downtime: {opt.get('est_downtime')}. {opt.get('tradeoff')}\n"
        system_prompt += "\n"

    system_prompt += (
        "Answer the user's questions clearly, concisely, and professionally. Use Markdown for formatting "
        "with lists, bold text, or code highlights where appropriate. Focus on technical, safety-conscious advice "
        "specifically relevant to the current system state. Avoid any conversational filler, warm introductions, "
        "or generic greetings (e.g. 'Sure, here is...', 'Hello engineer...'). Direct, professional engineering answers only.\n\n"
        "CRITICAL INSTRUCTION FOR REASONING AND LOGICAL CHAIN:\n"
        "First, write your reasoning process inside a <thinking>...</thinking> block. "
        "Your thinking process must read like brief, quick, professional engineering check-notes or mental checklist "
        "(e.g., '- Check if pressure is below relief valve limit of 90psi', '- Check for potential hose rupture due to RPM surge'). "
        "Keep the check-notes under 4-5 items. Do not use generic conversational text or explanations in the thinking block. "
        "After closing the thinking block with </thinking>, write your final engineering response. For example:\n"
        "<thinking>\n"
        "- Verify temperature warning threshold (80°C)\n"
        "- Check vibration deviation vs. shaft speed baseline\n"
        "- Assess oil pressure anomaly correlation\n"
        "</thinking>\n"
        "Here are the findings and actions:\n"
    )

    from flask import Response
    import requests
    import json

    if nvidia_key and (nvidia_model.startswith("nvidia/") or not gemini_key):
        payload_messages = [{"role": "system", "content": system_prompt}]
        if not messages:
            payload_messages.append({"role": "user", "content": "Hello! Please analyze the current system state."})
        else:
            for m in messages:
                role = m.get("role")
                if role == "model":
                    role = "assistant"
                payload_messages.append({"role": role, "content": m.get("content")})

        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {nvidia_key}"
        }
        body = {
            "model": nvidia_model,
            "messages": payload_messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": True
        }

        def generate_nvidia():
            try:
                response = requests.post(url, headers=headers, json=body, stream=True, timeout=20)
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'NVIDIA API error status {response.status_code}: {response.text}'})}\n\n"
                    return
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            if line_str == "data: [DONE]":
                                break
                            try:
                                chunk_data = json.loads(line_str[6:])
                                text_part = chunk_data["choices"][0]["delta"].get("content", "")
                                if text_part:
                                    yield f"data: {json.dumps({'text': text_part})}\n\n"
                            except Exception:
                                pass
            except Exception as e:
                yield f"data: {json.dumps({'error': f'Failed to stream from NVIDIA API: {str(e)}'})}\n\n"
                
        return Response(generate_nvidia(), mimetype="text/event-stream")

    elif gemini_key:
        def generate():
            try:
                import google.generativeai as genai
                from google.generativeai.types import GenerationConfig
                
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(
                    model_name=gemini_model,
                    system_instruction=system_prompt
                )
                
                contents = []
                if not messages:
                    contents.append({"role": "user", "parts": ["Hello! Please analyze the current system state."]})
                else:
                    for m in messages:
                        role = "user" if m.get("role") == "user" else "model"
                        contents.append({"role": role, "parts": [m.get("content")]})
                        
                response = model.generate_content_stream(
                    contents,
                    generation_config=GenerationConfig(
                        max_output_tokens=1000,
                        temperature=0.7
                    )
                )
                
                for chunk in response:
                    try:
                        text_part = chunk.text
                        if text_part:
                            yield f"data: {json.dumps({'text': text_part})}\n\n"
                    except Exception:
                        pass
            except Exception as e:
                yield f"data: {json.dumps({'error': f'Failed to stream from Gemini API: {str(e)}'})}\n\n"
                
        return Response(generate(), mimetype="text/event-stream")

    elif azure_key and azure_endpoint and azure_deployment:
        payload_messages = [{"role": "system", "content": system_prompt}]
        if not messages:
            payload_messages.append({"role": "user", "content": "Hello! Please analyze the current system state."})
        else:
            for m in messages:
                payload_messages.append({"role": m.get("role"), "content": m.get("content")})

        endpoint_clean = azure_endpoint.strip().rstrip("/")
        url = f"{endpoint_clean}/openai/deployments/{azure_deployment}/chat/completions?api-version={azure_version}"

        headers = {"Content-Type": "application/json", "api-key": azure_key}
        body = {"messages": payload_messages, "temperature": 0.7, "max_tokens": 1000, "stream": True}

        def generate_azure():
            try:
                response = requests.post(url, headers=headers, json=body, stream=True, timeout=20)
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'Azure API error status {response.status_code}: {response.text}'})}\n\n"
                    return
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            if line_str == "data: [DONE]":
                                break
                            try:
                                chunk_data = json.loads(line_str[6:])
                                text_part = chunk_data["choices"][0]["delta"].get("content", "")
                                if text_part:
                                    yield f"data: {json.dumps({'text': text_part})}\n\n"
                            except Exception:
                                pass
            except Exception as e:
                yield f"data: {json.dumps({'error': f'Failed to stream from Azure OpenAI: {str(e)}'})}\n\n"
                
        return Response(generate_azure(), mimetype="text/event-stream")

    def generate_unconfigured():
        msg = (
            "ℹ️ **AI Chat Backend has not been configured.**\n\n"
            "Please configure setup parameters:\n"
            "- Define `GEMINI_API_KEY` (Gemini model: e.g. `gemini-1.5-flash`)\n"
            "- Or configure `NVIDIA_API_KEY` (NVIDIA model: e.g. `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`)\n"
            "- Or configure Azure OpenAI settings in the dashboard sidebar or server environment."
        )
        yield f"data: {json.dumps({'text': msg})}\n\n"
    return Response(generate_unconfigured(), mimetype="text/event-stream")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)