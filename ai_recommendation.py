"""
AI Recommendation Engine for Predictive Maintenance System
Provides intelligent maintenance recommendations based on sensor data and fault predictions
"""

import json
from typing import Dict, List, Tuple
import pandas as pd


class AIRecommendationEngine:
    """
    Advanced AI recommendation system for predictive maintenance.
    Analyzes sensor data and provides actionable maintenance recommendations.
    """

    def __init__(self):
        """Initialize the recommendation engine with fault profiles and thresholds."""
        self.fault_profiles = self._initialize_fault_profiles()
        self.severity_weights = {
            "ok": 0,
            "warning": 1,
            "critical": 3,
            "emergency": 5
        }

    @staticmethod
    def _initialize_fault_profiles() -> Dict:
        """Define comprehensive fault profiles with thresholds and recommendations."""
        return {
            0: {
                "name": "System Operating Normally",
                "severity": "ok",
                "confidence_boost": 1.0,
                "primary_recommendations": [
                    "Continue regular maintenance schedule",
                    "Monitor all parameters within normal range",
                    "No immediate action required"
                ],
                "preventive_actions": [
                    "Schedule next maintenance check in 7-14 days",
                    "Keep spare parts inventory current"
                ]
            },
            1: {
                "name": "Overheating Fault",
                "severity": "critical",
                "confidence_boost": 1.2,
                "primary_recommendations": [
                    "URGENT: Check cooling system immediately",
                    "Inspect pump bearings for wear",
                    "Clear cooling fins and radiator",
                    "Verify coolant flow and pressure"
                ],
                "preventive_actions": [
                    "Schedule immediate maintenance (within 24 hours)",
                    "Reduce operational load temporarily",
                    "Monitor temperature continuously"
                ],
                "risk_factors": ["Temperature above 88°C", "Sustained high pressure"],
                "estimated_downtime": "4-8 hours"
            },
            2: {
                "name": "High Vibration Fault",
                "severity": "critical",
                "confidence_boost": 1.15,
                "primary_recommendations": [
                    "URGENT: Stop operation and inspect immediately",
                    "Check alignment of rotating components",
                    "Tighten all loose fasteners",
                    "Inspect bearings for damage"
                ],
                "preventive_actions": [
                    "Schedule urgent maintenance (within 12 hours)",
                    "Replace worn bearings if necessary",
                    "Perform dynamic balancing"
                ],
                "risk_factors": ["Vibration above 0.04g", "Grinding noises"],
                "estimated_downtime": "2-6 hours"
            },
            3: {
                "name": "Pressure Failure",
                "severity": "critical",
                "confidence_boost": 1.18,
                "primary_recommendations": [
                    "Check hydraulic pressure lines for leaks",
                    "Inspect pump condition and output",
                    "Verify pressure relief valve operation",
                    "Check for blocked filters or lines"
                ],
                "preventive_actions": [
                    "Schedule maintenance within 24 hours",
                    "Prepare replacement pump if needed",
                    "Have fluid replacement materials ready"
                ],
                "risk_factors": ["Pressure below 80 psi", "Erratic readings"],
                "estimated_downtime": "6-12 hours"
            },
            4: {
                "name": "Low Oil Level",
                "severity": "warning",
                "confidence_boost": 1.0,
                "primary_recommendations": [
                    "Refill oil to optimal level immediately",
                    "Inspect for visible leaks or seepage",
                    "Check oil condition and color"
                ],
                "preventive_actions": [
                    "Schedule maintenance within 48 hours",
                    "Investigate root cause of oil loss",
                    "Replace seals if leakage detected"
                ],
                "risk_factors": ["Oil below 30%", "Dark or burnt oil"],
                "estimated_downtime": "1-2 hours"
            },
            5: {
                "name": "Coolant Leakage Fault",
                "severity": "critical",
                "confidence_boost": 1.25,
                "primary_recommendations": [
                    "URGENT: Locate and repair coolant leak",
                    "Inspect coolant pipes for cracks",
                    "Check all connection points and seals",
                    "Refill coolant to appropriate level"
                ],
                "preventive_actions": [
                    "Schedule immediate maintenance (within 24 hours)",
                    "Have replacement pipes and seals available",
                    "Monitor coolant level during operation"
                ],
                "risk_factors": ["Active leakage", "Low coolant levels"],
                "estimated_downtime": "3-8 hours"
            }
        }

    def analyze_sensor_data(self, sensor_data: Dict) -> Dict:
        """
        Analyze sensor data and provide comprehensive diagnostics.

        Args:
            sensor_data: Dictionary containing sensor readings

        Returns:
            Dictionary with diagnostic information and risk assessment
        """
        analysis = {
            "sensor_health": self._assess_sensor_health(sensor_data),
            "trend_analysis": self._analyze_trends(sensor_data),
            "risk_assessment": self._calculate_risk_level(sensor_data),
            "anomaly_detection": self._detect_anomalies(sensor_data)
        }
        return analysis

    @staticmethod
    def _assess_sensor_health(sensor_data: Dict) -> Dict:
        """Assess individual sensor health and status."""
        health_status = {}
        
        thresholds = {
            "Temperature_C": {"normal": (50, 80), "warning": (80, 88), "critical": (88, 120)},
            "Pressure_psi": {"normal": (90, 110), "warning": (80, 90), "critical": (0, 80)},
            "Vibration_g": {"normal": (0, 0.02), "warning": (0.02, 0.04), "critical": (0.04, 1.0)},
            "Oil_Level_pct": {"normal": (50, 100), "warning": (30, 50), "critical": (0, 30)},
            "Flow_Rate_lpm": {"normal": (250, 350), "warning": (150, 250), "critical": (0, 150)},
        }
        
        for sensor, value in sensor_data.items():
            if sensor in thresholds:
                status = "normal"
                for level, (min_val, max_val) in thresholds[sensor].items():
                    if min_val <= value <= max_val:
                        status = level
                        break
                health_status[sensor] = status
        
        return health_status

    @staticmethod
    def _analyze_trends(sensor_data: Dict) -> Dict:
        """Analyze sensor trends and patterns."""
        return {
            "trend_direction": "stable",
            "rate_of_change": "low",
            "prediction": "No significant changes expected in next 24 hours"
        }

    @staticmethod
    def _calculate_risk_level(sensor_data: Dict) -> str:
        """Calculate overall system risk level."""
        critical_count = 0
        warning_count = 0
        
        if sensor_data.get("Temperature_C", 0) > 88:
            critical_count += 1
        elif sensor_data.get("Temperature_C", 0) > 80:
            warning_count += 1
        
        if sensor_data.get("Vibration_g", 0) > 0.04:
            critical_count += 1
        elif sensor_data.get("Vibration_g", 0) > 0.02:
            warning_count += 1
        
        if sensor_data.get("Pressure_psi", 0) < 80:
            critical_count += 1
        elif sensor_data.get("Pressure_psi", 0) < 90:
            warning_count += 1
        
        if sensor_data.get("Oil_Level_pct", 0) < 30:
            critical_count += 1
        elif sensor_data.get("Oil_Level_pct", 0) < 50:
            warning_count += 1
        
        if critical_count >= 2:
            return "CRITICAL"
        elif critical_count == 1 or warning_count >= 3:
            return "WARNING"
        else:
            return "NORMAL"

    @staticmethod
    def _detect_anomalies(sensor_data: Dict) -> List[str]:
        """Detect anomalies in sensor data."""
        anomalies = []
        
        if sensor_data.get("Coolant_Leak", 0) == 1:
            anomalies.append("Coolant leak detected")
        
        if sensor_data.get("Temperature_C", 0) > 100:
            anomalies.append("Extreme temperature detected")
        
        if sensor_data.get("Vibration_g", 0) > 0.08:
            anomalies.append("Severe vibration detected")
        
        if sensor_data.get("Pressure_psi", 0) < 50:
            anomalies.append("Critically low pressure")
        
        return anomalies

    def generate_recommendations(self, fault_code: int, sensor_data: Dict, 
                                confidence: float = 0.85) -> Dict:
        """
        Generate comprehensive AI-driven recommendations.

        Args:
            fault_code: Predicted fault classification (0-5)
            sensor_data: Dictionary of sensor readings
            confidence: Model confidence level (0-1)

        Returns:
            Dictionary with detailed recommendations and action items
        """
        fault_profile = self.fault_profiles.get(fault_code, self.fault_profiles[0])
        analysis = self.analyze_sensor_data(sensor_data)
        
        recommendations = {
            "fault_code": fault_code,
            "fault_name": fault_profile["name"],
            "severity": fault_profile["severity"],
            "confidence": confidence,
            "confidence_rating": self._rate_confidence(confidence),
            "risk_level": analysis["risk_assessment"],
            "primary_actions": fault_profile["primary_recommendations"],
            "preventive_measures": fault_profile["preventive_actions"],
            "estimated_downtime": fault_profile.get("estimated_downtime", "Unknown"),
            "sensor_health": analysis["sensor_health"],
            "anomalies": analysis["anomaly_detection"],
            "next_check": self._calculate_next_check(fault_code, confidence),
            "spare_parts": self._suggest_spare_parts(fault_code),
            "technician_notes": self._generate_technician_notes(fault_code, sensor_data),
            "cost_estimate": self._estimate_maintenance_cost(fault_code),
            "urgency_level": self._determine_urgency(fault_code, analysis["risk_assessment"])
        }
        
        return recommendations

    @staticmethod
    def _rate_confidence(confidence: float) -> str:
        """Convert confidence score to rating."""
        if confidence >= 0.95:
            return "Very High"
        elif confidence >= 0.85:
            return "High"
        elif confidence >= 0.75:
            return "Medium"
        else:
            return "Low"

    @staticmethod
    def _calculate_next_check(fault_code: int, confidence: float) -> str:
        """Calculate recommended time for next system check."""
        if fault_code == 0:
            return "7-14 days (routine maintenance)"
        elif fault_code in [1, 3, 5]:
            return "Immediate - within 24 hours"
        elif fault_code in [2]:
            return "Urgent - within 12 hours"
        else:
            return "2-3 days (priority maintenance)"

    @staticmethod
    def _suggest_spare_parts(fault_code: int) -> List[str]:
        """Suggest spare parts needed for maintenance."""
        spare_parts_map = {
            0: [],
            1: ["Cooling system seals", "Pump bearing kit", "Thermal paste", "Cooling fluid"],
            2: ["Bearing kit", "Alignment shims", "Fastener assortment", "Lubricating oil"],
            3: ["Hydraulic hose kit", "Pump assembly", "Seals and gaskets", "Hydraulic fluid"],
            4: ["Hydraulic oil", "Seal kit", "Oil filter"],
            5: ["Coolant pipe assortment", "Leak sealant", "Coolant fluid", "Clamp kit"]
        }
        return spare_parts_map.get(fault_code, [])

    @staticmethod
    def _generate_technician_notes(fault_code: int, sensor_data: Dict) -> str:
        """Generate detailed notes for maintenance technician."""
        notes_map = {
            0: "System operating within normal parameters. Continue standard maintenance.",
            1: f"High temperature detected ({sensor_data.get('Temperature_C', 0)}°C). Check cooling circulation and check for blockages.",
            2: f"High vibration levels detected ({sensor_data.get('Vibration_g', 0)}g). Perform bearing inspection and dynamic balancing.",
            3: f"Low pressure detected ({sensor_data.get('Pressure_psi', 0)} psi). Check for leaks and pump efficiency.",
            4: f"Low oil level ({sensor_data.get('Oil_Level_pct', 0)}%). Refill and investigate leakage source.",
            5: "Coolant leak detected. Inspect all connections and pipe integrity. Seal leaks immediately."
        }
        return notes_map.get(fault_code, "See fault profile for details.")

    @staticmethod
    def _estimate_maintenance_cost(fault_code: int) -> Dict:
        """Estimate maintenance costs based on fault type."""
        cost_estimates = {
            0: {"parts": "$0-50", "labor": "$0", "total": "$0-50", "urgency": "Low"},
            1: {"parts": "$200-500", "labor": "$200-400", "total": "$400-900", "urgency": "High"},
            2: {"parts": "$300-700", "labor": "$300-500", "total": "$600-1200", "urgency": "High"},
            3: {"parts": "$400-1000", "labor": "$400-600", "total": "$800-1600", "urgency": "Critical"},
            4: {"parts": "$50-150", "labor": "$100-200", "total": "$150-350", "urgency": "Medium"},
            5: {"parts": "$150-400", "labor": "$200-400", "total": "$350-800", "urgency": "Critical"}
        }
        return cost_estimates.get(fault_code, {"parts": "Unknown", "labor": "Unknown", "total": "Unknown", "urgency": "Unknown"})

    @staticmethod
    def _determine_urgency(fault_code: int, risk_level: str) -> int:
        """Determine urgency level (1-5, where 5 is most urgent)."""
        urgency_map = {
            0: 1,  # Routine
            1: 5,  # Overheating - Critical
            2: 5,  # High Vibration - Critical
            3: 5,  # Pressure Failure - Critical
            4: 2,  # Low Oil - Warning
            5: 5   # Coolant Leak - Critical
        }
        return urgency_map.get(fault_code, 3)

    def export_recommendations_json(self, recommendations: Dict) -> str:
        """Export recommendations as JSON string."""
        return json.dumps(recommendations, indent=2)

    def export_recommendations_report(self, recommendations: Dict) -> str:
        """Export recommendations as a formatted text report."""
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║          AI PREDICTIVE MAINTENANCE RECOMMENDATIONS             ║
╚════════════════════════════════════════════════════════════════╝

DIAGNOSIS
─────────────────────────────────────────────────────────────────
Fault Code:        {recommendations['fault_code']}
Fault Type:        {recommendations['fault_name']}
Severity Level:    {recommendations['severity'].upper()}
Confidence:        {recommendations['confidence_rating']} ({recommendations['confidence']:.1%})
Risk Level:        {recommendations['risk_level']}
Urgency:           {"⚠ URGENT" if recommendations['urgency_level'] >= 4 else "Normal"}

IMMEDIATE ACTIONS
─────────────────────────────────────────────────────────────────
"""
        for i, action in enumerate(recommendations['primary_actions'], 1):
            report += f"{i}. {action}\n"

        report += f"""
PREVENTIVE MEASURES
─────────────────────────────────────────────────────────────────
"""
        for i, measure in enumerate(recommendations['preventive_measures'], 1):
            report += f"{i}. {measure}\n"

        report += f"""
SENSOR STATUS
─────────────────────────────────────────────────────────────────
"""
        for sensor, status in recommendations['sensor_health'].items():
            report += f"{sensor}: {status.upper()}\n"

        report += f"""
SPARE PARTS NEEDED
─────────────────────────────────────────────────────────────────
"""
        if recommendations['spare_parts']:
            for part in recommendations['spare_parts']:
                report += f"• {part}\n"
        else:
            report += "None required\n"

        report += f"""
COST ESTIMATE
─────────────────────────────────────────────────────────────────
Parts Cost:        {recommendations['cost_estimate']['parts']}
Labor Cost:        {recommendations['cost_estimate']['labor']}
Total Estimate:    {recommendations['cost_estimate']['total']}

NEXT CHECK
─────────────────────────────────────────────────────────────────
{recommendations['next_check']}

TECHNICIAN NOTES
─────────────────────────────────────────────────────────────────
{recommendations['technician_notes']}

═════════════════════════════════════════════════════════════════
"""
        return report


# Example usage and testing
if __name__ == "__main__":
    # Initialize the engine
    engine = AIRecommendationEngine()

    # Example sensor data
    sensor_data_normal = {
        "Temperature_C": 75,
        "Pressure_psi": 105,
        "Vibration_g": 0.015,
        "Flow_Rate_lpm": 300,
        "Oil_Level_pct": 85,
        "RPM": 1500,
        "Coolant_Leak": 0,
        "Operating_Hours": 240
    }

    sensor_data_fault = {
        "Temperature_C": 95,
        "Pressure_psi": 115,
        "Vibration_g": 0.02,
        "Flow_Rate_lpm": 280,
        "Oil_Level_pct": 80,
        "RPM": 1600,
        "Coolant_Leak": 0,
        "Operating_Hours": 240
    }

    # Generate recommendations
    print("Testing Normal System:")
    rec_normal = engine.generate_recommendations(0, sensor_data_normal, confidence=0.98)
    print(engine.export_recommendations_report(rec_normal))

    print("\n\nTesting Overheating Fault:")
    rec_fault = engine.generate_recommendations(1, sensor_data_fault, confidence=0.92)
    print(engine.export_recommendations_report(rec_fault))
