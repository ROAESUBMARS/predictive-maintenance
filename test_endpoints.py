import os
os.environ["DEV_BYPASS_TOKEN"] = "admin"

import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clear_rate_limits():
    from app import _rate_limit_records
    _rate_limit_records.clear()

@pytest.fixture
def tech_token(client):
    payload = {"email": "sarah@nmu.edu.ng", "password": "admin", "role": "tech"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 200
    return response.json["token"]

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json
    assert data["status"] == "ok"

def test_predict_normal(client):
    payload = {
        "Temperature_C": 70,
        "Pressure_psi": 100,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": "Bearer admin"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert data["fault_code"] == 0
    assert "System Operating Normally" in data["fault"]

def test_predict_overheating(client):
    payload = {
        "Temperature_C": 95,
        "Pressure_psi": 120,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": "Bearer admin"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert data["fault_code"] == 1
    assert "Overheating" in data["fault"]

def test_chat_unconfigured(client, monkeypatch):
    import dotenv
    monkeypatch.setattr(dotenv, "load_dotenv", lambda **k: None)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    payload = {
        "messages": [],
        "sensor_data": {},
        "diagnosis": {},
        "azure_config": {}
    }
    headers = {"Authorization": "Bearer admin"}
    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert "data: " in content
    assert "AI Chat Backend has not been configured" in content

def test_chat_reject_client_keys(client):
    headers = {"Authorization": "Bearer admin"}
    
    # 1. Try sending gemini_api_key in request body
    payload_gemini = {
        "messages": [],
        "sensor_data": {},
        "diagnosis": {},
        "gemini_api_key": "hacker_key_here"
    }
    response = client.post("/chat", json=payload_gemini, headers=headers)
    assert response.status_code == 400
    assert "Provider API keys must be configured server-side" in response.json["error"]

    # 2. Try sending azure_config with api_key in request body
    payload_azure = {
        "messages": [],
        "sensor_data": {},
        "diagnosis": {},
        "azure_config": {"api_key": "hacker_key_here"}
    }
    response = client.post("/chat", json=payload_azure, headers=headers)
    assert response.status_code == 400
    assert "Provider API keys must be configured server-side" in response.json["error"]

def test_unauthorized_access(client):
    payload = {
        "Temperature_C": 70,
        "Pressure_psi": 100,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    # Send request without headers
    response = client.post("/predict", json=payload)
    assert response.status_code == 401
    
    # Send request with invalid header password
    headers = {"Authorization": "Bearer wrongpassword"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 401

def test_login_flow(client):
    # 1. Successful login
    payload = {"email": "sarah@nmu.edu.ng", "password": "admin", "role": "tech"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 200
    data = response.json
    assert "token" in data
    
    # 2. Mismatched role login
    payload = {"email": "sarah@nmu.edu.ng", "password": "admin", "role": "eng"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 403
    
    # 3. Invalid email login
    payload = {"email": "unknown@nmu.edu.ng", "password": "admin", "role": "tech"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 401

    # 4. Invalid password login
    payload = {"email": "sarah@nmu.edu.ng", "password": "wrongpassword", "role": "tech"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 401

def test_rbac_config(client, tech_token):
    # 1. Login as Engineer
    payload = {"email": "eng@nmu.edu.ng", "password": "admin", "role": "eng"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 200
    eng_token = response.json["token"]

    # 2. Try accessing /api/config GET as Technician -> should be 403 Forbidden
    headers = {"Authorization": f"Bearer {tech_token}"}
    response = client.get("/api/config", headers=headers)
    assert response.status_code == 403

    # 3. Try accessing /api/config GET as Engineer -> should be 200 OK
    headers = {"Authorization": f"Bearer {eng_token}"}
    response = client.get("/api/config", headers=headers)
    assert response.status_code == 200
    config_data = response.json
    assert "GEMINI_API_KEY" in config_data
    
    key_val = config_data["GEMINI_API_KEY"]
    assert key_val == "" or "..." in key_val or key_val == "******", "Sensitive keys must be masked"

    # 4. Try updating /api/config POST as Technician -> should be 403 Forbidden
    response = client.post("/api/config", json={"GEMINI_MODEL": "gemini-ultra"}, headers={"Authorization": f"Bearer {tech_token}"})
    assert response.status_code == 403

    # 5. Try updating /api/config POST as Engineer -> should be 200 OK
    response = client.post("/api/config", json={"GEMINI_MODEL": "gemini-flash-lite-latest"}, headers={"Authorization": f"Bearer {eng_token}"})
    assert response.status_code == 200

def test_chat_unauthorized(client):
    payload = {
        "messages": [],
        "sensor_data": {},
        "diagnosis": {},
        "azure_config": {}
    }
    # Send request without headers
    response = client.post("/chat", json=payload)
    assert response.status_code == 401
    
    # Send request with invalid header password
    headers = {"Authorization": "Bearer wrongpassword"}
    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 401

def test_rate_limiter(client, tech_token):
    payload = {
        "Temperature_C": 70,
        "Pressure_psi": 100,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    
    # Make 120 successful requests
    for i in range(120):
        response = client.post("/predict", json=payload, headers=headers)
        assert response.status_code != 429
        
    # The 121st request must be rate-limited and return 429
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json["error"]

def test_x_admin_key_auth(client):
    payload = {
        "Temperature_C": 70,
        "Pressure_psi": 100,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    # Test authentication using the X-Admin-Key header
    headers = {"X-Admin-Key": "admin"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json["fault_code"] == 0

def test_rejected_forged_tokens(client):
    from itsdangerous import URLSafeTimedSerializer
    
    # 1. Sign a token using the old compromised hardcoded secret key
    old_secret = "nmu-predictive-maintenance-secret-key-129837"
    serializer_old = URLSafeTimedSerializer(old_secret)
    token_forged = serializer_old.dumps({"email": "eng@nmu.edu.ng", "role": "eng"})
    
    # 2. Prepare request with forged token
    payload = {
        "Temperature_C": 70,
        "Pressure_psi": 100,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": f"Bearer {token_forged}"}
    
    # 3. Attempt request -> should be rejected with 401 Unauthorized
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 401
    assert "Unauthorized" in response.json["error"]

def test_admin_password_rejected_as_token(client):
    # Save current bypass token
    orig_bypass = os.environ.get("DEV_BYPASS_TOKEN")
    
    # 1. Change the DEV_BYPASS_TOKEN to some secure secret
    os.environ["DEV_BYPASS_TOKEN"] = "super-secret-secure-bypass-token"
    
    try:
        # 2. Try accessing with the old default 'admin' bypass
        payload = {
            "Temperature_C": 70,
            "Pressure_psi": 100,
            "Vibration_g": 0.02,
            "Flow_Rate_lpm": 300,
            "Oil_Level_pct": 60,
            "RPM": 1500,
            "Coolant_Leak": 0,
            "Operating_Hours": 100
        }
        headers = {"Authorization": "Bearer admin"}
        response = client.post("/predict", json=payload, headers=headers)
        
        # Should be rejected because 'admin' is no longer the bypass token
        assert response.status_code == 401
        assert "Unauthorized" in response.json["error"]
        
    finally:
        # Restore the original token
        if orig_bypass is not None:
            os.environ["DEV_BYPASS_TOKEN"] = orig_bypass
        else:
            del os.environ["DEV_BYPASS_TOKEN"]

def test_rate_limiter_recommend(client, tech_token):
    payload = {
        "Temperature_C": 70,
        "Pressure_psi": 100,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    
    # Make 30 successful requests to /recommend
    for i in range(30):
        response = client.post("/recommend", json=payload, headers=headers)
        assert response.status_code != 429
        
    # The 31st request must be rate-limited and return 429
    response = client.post("/recommend", json=payload, headers=headers)
    assert response.status_code == 429

def test_rate_limiter_schedule(client, tech_token):
    payload = {
        "fault_code": 0,
        "confidence": 1.0,
        "operating_hours": 100
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    
    # Make 120 successful requests to /schedule
    for i in range(120):
        response = client.post("/schedule", json=payload, headers=headers)
        assert response.status_code != 429
        
    # The 121st request must be rate-limited and return 429
    response = client.post("/schedule", json=payload, headers=headers)
    assert response.status_code == 429

def test_post_diagnostic_decision_matrix(client, tech_token):
    payload = {
        "Temperature_C": 96,
        "Pressure_psi": 125,
        "Vibration_g": 0.05,
        "Flow_Rate_lpm": 280,
        "Oil_Level_pct": 55,
        "RPM": 1600,
        "Coolant_Leak": 0,
        "Operating_Hours": 240
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    ai = data["ai_recommendation"]
    
    assert "rul_info" in ai
    assert "rul_hours" in ai["rul_info"]
    assert "decision_matrix" in ai
    assert len(ai["decision_matrix"]) >= 2
    assert "root_causes" in ai
    assert len(ai["root_causes"]) >= 1
    assert "cascading_risks" in ai

def test_alert_email_matching_check(client, tech_token):
    payload = {
        "Temperature_C": 95,
        "Pressure_psi": 120,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100,
        "alert_email": "sarah@nmu.edu.ng"
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    
    # 1. Alerting self is allowed -> should return 200
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    
    # 2. Alerting self in /recommend is allowed -> should return 200
    response = client.post("/recommend", json=payload, headers=headers)
    assert response.status_code == 200
    
    # 3. Alerting someone else is Forbidden -> should return 403
    payload["alert_email"] = "stranger@nmu.edu.ng"
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json["error"]
    
    response = client.post("/recommend", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json["error"]


def test_procurement_nominal_rul(client):
    payload = {
        "rul_hours": 720.0,
        "fault_code": 0,
        "threshold_hours": 48.0
    }
    headers = {"Authorization": "Bearer admin"}
    response = client.post("/api/procurement", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert data["procurement_required"] is False
    assert data["suggested_work_order"] is None


def test_procurement_low_rul_trigger(client, tech_token):
    # Test low RUL via /predict with overheating fault
    payload = {
        "Temperature_C": 95,
        "Pressure_psi": 120,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert "suggested_procurement" in data
    sp = data["suggested_procurement"]
    assert sp["procurement_required"] is True
    assert sp["rul_hours"] < 48.0
    assert len(sp["parts_list"]) >= 1
    assert "lead_time_warning" in sp
    assert sp["suggested_work_order"]["wo_id"].startswith("SWO-PROC-")


def test_api_procurement_custom_threshold(client):
    # Test custom threshold of 100.0 hours
    payload = {
        "rul_hours": 75.0,
        "fault_code": 2,
        "threshold_hours": 100.0
    }
    headers = {"Authorization": "Bearer admin"}
    response = client.post("/api/procurement", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert data["procurement_required"] is True
    assert data["threshold_hours"] == 100.0
    assert len(data["parts_list"]) >= 1
    assert "Replacement Roller Bearings" in [p["name"] for p in data["parts_list"]]


def test_cii_nominal_baseline(client, tech_token):
    payload = {
        "Temperature_C": 70,
        "Pressure_psi": 100,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert "cii_emissions" in data
    cii = data["cii_emissions"]
    assert cii["cii_rating"] == "A"
    assert cii["excess_power_kw"] == 0.0
    assert cii["compliance_warning"] is None


def test_cii_degraded_fault_impact(client, tech_token):
    # Test high vibration fault causing efficiency drop & CII rating degradation
    payload = {
        "Temperature_C": 85,
        "Pressure_psi": 90,
        "Vibration_g": 0.08,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 60,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 100
    }
    headers = {"Authorization": f"Bearer {tech_token}"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert "cii_emissions" in data
    cii = data["cii_emissions"]
    assert cii["cii_rating"] in ["D", "E"]
    assert cii["excess_power_kw"] > 10.0
    assert cii["excess_fuel_kg_per_day"] > 50.0
    assert cii["excess_co2_kg_per_day"] > 150.0
    assert cii["compliance_warning"] is not None
    assert "IMO COMPLIANCE ALERT" in cii["compliance_warning"]


def test_api_cii_emissions_endpoint(client):
    payload = {
        "fault_code": 1,
        "sensor_data": {"Temperature_C": 92.0, "Vibration_g": 0.04}
    }
    headers = {"Authorization": "Bearer admin"}
    response = client.post("/api/cii-emissions", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json
    assert "cii_rating" in data
    assert "excess_power_kw" in data
    assert "decarbonization_action" in data







