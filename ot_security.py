import time
import logging
from collections import defaultdict
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Standard physical sanity bounds for marine auxiliary machinery telemetry
PHYSICAL_TELEMETRY_BOUNDS = {
    "Temperature_C": {"min": -30.0, "max": 150.0, "unit": "°C"},
    "Pressure_psi": {"min": 0.0, "max": 350.0, "unit": "psi"},
    "Vibration_g": {"min": 0.0, "max": 0.5, "unit": "g"},
    "Flow_Rate_lpm": {"min": 0.0, "max": 1000.0, "unit": "lpm"},
    "Oil_Level_pct": {"min": 0.0, "max": 100.0, "unit": "%"},
    "RPM": {"min": 0.0, "max": 5000.0, "unit": "RPM"},
    "Coolant_Leak": {"allowed_values": [0, 1]},
    "Operating_Hours": {"min": 0.0, "max": 500000.0, "unit": "hrs"}
}

class OTSecurityMonitor:
    """
    Operational Technology (OT) & Telemetry Cybersecurity Anomaly Detector.
    Monitors sensor telemetry data pipelines for out-of-bounds physical spoofing,
    unauthorized network access attempts, and burst traffic anomalies.
    """
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.packets_scanned = 0
        self.anomalies_detected = 0
        self.unauthorized_access_count = 0
        self._ip_failed_attempts = defaultdict(list)
        self.threat_level = "LOW"  # LOW, MEDIUM, HIGH

    def inspect_telemetry_payload(self, sensor_data: Dict[str, Any], client_ip: str = "127.0.0.1") -> Dict[str, Any]:
        """
        Inspects incoming sensor telemetry for physical plausibility anomalies (e.g. sensor spoofing, MITM injection).
        """
        self.packets_scanned += 1
        anomalies = []
        
        for key, bounds in PHYSICAL_TELEMETRY_BOUNDS.items():
            if key in sensor_data:
                val = sensor_data[key]
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    anomalies.append({
                        "parameter": key,
                        "value": sensor_data[key],
                        "type": "MALFORMED_DATA_TYPE",
                        "severity": "HIGH",
                        "details": f"Parameter '{key}' has non-numeric value '{sensor_data[key]}'"
                    })
                    continue

                if "allowed_values" in bounds:
                    if int(val) not in bounds["allowed_values"]:
                        anomalies.append({
                            "parameter": key,
                            "value": val,
                            "type": "INVALID_DISCRETE_STATE",
                            "severity": "HIGH",
                            "details": f"Discrete state '{key}' value {val} not in allowed set {bounds['allowed_values']}"
                        })
                else:
                    if val < bounds["min"] or val > bounds["max"]:
                        anomalies.append({
                            "parameter": key,
                            "value": val,
                            "type": "OUT_OF_PHYSICAL_BOUNDS",
                            "severity": "CRITICAL",
                            "details": f"Value {val}{bounds['unit']} violates physical limits ({bounds['min']} to {bounds['max']}{bounds['unit']})"
                        })

        is_anomalous = len(anomalies) > 0
        if is_anomalous:
            self.anomalies_detected += len(anomalies)
            self._update_threat_level()
            
            event = {
                "timestamp": time.time(),
                "event_type": "OT_TELEMETRY_SPOOFING_ANOMALY",
                "client_ip": client_ip,
                "threat_level": self.threat_level,
                "anomalies": anomalies
            }
            self.audit_log.insert(0, event)
            if len(self.audit_log) > 100:
                self.audit_log.pop()
                
            logger.warning(f"[OT SECURITY ANOMALY DETECTED] IP: {client_ip} | Anomalies: {len(anomalies)}")

        return {
            "is_valid": not is_anomalous,
            "anomalies": anomalies,
            "threat_level": self.threat_level
        }

    def record_access_event(self, client_ip: str, endpoint: str, success: bool, reason: str = ""):
        """
        Tracks authentication and network traffic patterns to detect brute-force or unauthorized penetration attempts.
        """
        now = time.time()
        if not success:
            self.unauthorized_access_count += 1
            self._ip_failed_attempts[client_ip].append(now)
            
            # Prune attempts older than 5 minutes
            self._ip_failed_attempts[client_ip] = [
                t for t in self._ip_failed_attempts[client_ip] if now - t < 300
            ]
            
            attempt_count = len(self._ip_failed_attempts[client_ip])
            if attempt_count >= 5:
                self._update_threat_level(elevate=True)
                event = {
                    "timestamp": now,
                    "event_type": "UNAUTHORIZED_BURST_ACCESS_ATTEMPT",
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "threat_level": self.threat_level,
                    "reason": f"Multiple authentication failures ({attempt_count} attempts in 5m): {reason}"
                }
                self.audit_log.insert(0, event)
                if len(self.audit_log) > 100:
                    self.audit_log.pop()
                    
                logger.warning(f"[OT SECURITY ACCESS WARNING] IP: {client_ip} | Endpoint: {endpoint} | Reason: {reason}")

    def _update_threat_level(self, elevate: bool = False):
        if elevate or self.anomalies_detected > 10 or self.unauthorized_access_count > 15:
            self.threat_level = "HIGH"
        elif self.anomalies_detected > 0 or self.unauthorized_access_count > 3:
            self.threat_level = "MEDIUM"
        else:
            self.threat_level = "LOW"

    def get_security_summary(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "threat_level": self.threat_level,
            "packets_scanned": self.packets_scanned,
            "anomalies_detected": self.anomalies_detected,
            "unauthorized_access_attempts": self.unauthorized_access_count,
            "audit_log": self.audit_log[:10],
            "recommendations": self._get_security_recommendations()
        }

    def _get_security_recommendations(self) -> List[str]:
        recs = [
            "Enforce TLS 1.3 encryption on all Modbus TCP / MQTT telemetry gateways.",
            "Verify cryptographic HMAC signatures on physical sensor payload headers.",
            "Segment OT machinery networks from corporate IT networks using zero-trust firewalls."
        ]
        if self.threat_level == "HIGH":
            recs.insert(0, "CRITICAL: High threat detected. Isolate suspected OT sensor node and trigger credential rotation.")
        return recs

# Global singleton monitor instance
ot_monitor = OTSecurityMonitor()
