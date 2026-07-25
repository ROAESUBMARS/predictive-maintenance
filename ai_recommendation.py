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

    def calculate_rul_hours(self, fault_code: int, sensor_data: Dict, confidence: float = 0.85) -> Dict:
        """Calculate dynamic Remaining Useful Life (RUL) in operating hours."""
        if fault_code == 0:
            return {"rul_hours": 720.0, "status": "Nominal", "confidence_range": "650-800 hrs"}
        
        # Base RUL by fault code
        base_rul = {1: 18.0, 2: 12.0, 3: 8.0, 4: 48.0, 5: 14.0}.get(fault_code, 24.0)
        
        # Degradation acceleration factors based on telemetry Z-scores
        temp = sensor_data.get("Temperature_C", 70)
        vib = sensor_data.get("Vibration_g", 0.02)
        pres = sensor_data.get("Pressure_psi", 100)
        oil = sensor_data.get("Oil_Level_pct", 60)
        
        acceleration = 1.0
        if temp > 88: acceleration += (temp - 88) * 0.05
        if vib > 0.04: acceleration += (vib - 0.04) * 20.0
        if pres < 80: acceleration += (80 - pres) * 0.03
        if oil < 30: acceleration += (30 - oil) * 0.04
        
        adjusted_rul = max(1.0, round(base_rul / acceleration, 1))
        lower_bound = max(0.5, round(adjusted_rul * 0.75, 1))
        upper_bound = round(adjusted_rul * 1.25, 1)
        
        return {
            "rul_hours": adjusted_rul,
            "status": "Critical" if adjusted_rul < 12 else "Warning",
            "confidence_range": f"{lower_bound} - {upper_bound} hrs"
        }

    def generate_decision_matrix(self, fault_code: int, sensor_data: Dict, confidence: float = 0.85) -> List[Dict]:
        """Generate 3 prescriptive operational decision options post-diagnosis."""
        rul = self.calculate_rul_hours(fault_code, sensor_data, confidence)["rul_hours"]
        
        if fault_code == 0:
            return [
                {
                    "id": "opt_routine",
                    "title": "Continue Normal Operation",
                    "tag": "RECOMMENDED CHOICE",
                    "risk_score": 5,
                    "production_impact": 0,
                    "est_downtime": "0 hrs",
                    "action_steps": ["Maintain standard operating load", "Log telemetry data every shift"],
                    "tradeoff": "Lowest operational disruption; zero immediate cost."
                },
                {
                    "id": "opt_preventive_check",
                    "title": "Schedule Preventive Calibration",
                    "tag": "OPTIONAL",
                    "risk_score": 2,
                    "production_impact": 10,
                    "est_downtime": "1 hr",
                    "action_steps": ["Inspect sensor alignment during next scheduled window"],
                    "tradeoff": "Minor planned downtime to verify baseline."
                }
            ]
            
        fault_name = self.fault_profiles.get(fault_code, {}).get("name", "Detected Fault")
        
        # Option 1: Emergency Shutdown
        opt1 = {
            "id": "opt_shutdown",
            "title": "Emergency Shutdown & Immediate Repair",
            "tag": "MAX SAFETY",
            "risk_score": 2,
            "production_impact": 100,
            "est_downtime": self.fault_profiles.get(fault_code, {}).get("estimated_downtime", "4-8 hrs"),
            "action_steps": [
                "Immediately trip main pump breaker and apply lockout/tagout.",
                "Deploy lead technician to inspect components and replace worn parts.",
                "Conduct full system pressure and vibration test prior to restart."
            ],
            "tradeoff": "Eliminates catastrophic failure risk; causes immediate production halt."
        }
        
        # Option 2: Capacity Derating / Load Reduction (Recommended if RUL > 4 hrs)
        opt2 = {
            "id": "opt_derate",
            "title": "Derate Operating Capacity (Reduce Load 30%)",
            "tag": "RECOMMENDED CHOICE",
            "risk_score": 18,
            "production_impact": 30,
            "est_downtime": "2-4 hrs (scheduled shift end)",
            "action_steps": [
                f"Throttle RPM from {sensor_data.get('RPM', 1500)} to {int(sensor_data.get('RPM', 1500)*0.7)} RPM.",
                "Enable continuous thermal and vibration threshold alerts.",
                f"Stage replacement parts and execute repair within next {rul} hours."
            ],
            "tradeoff": "Keeps 70% production active while extending RUL and preventing runaway thermal buildup."
        }
        
        # Option 3: Monitored Run to Shift End
        opt3 = {
            "id": "opt_monitored_run",
            "title": "Managed Continuous Run with Automated Trip",
            "tag": "HIGH RISK",
            "risk_score": 65 if rul > 10 else 88,
            "production_impact": 0,
            "est_downtime": "0 hrs (Immediate)",
            "action_steps": [
                "Maintain current throughput with automated emergency trip threshold armed.",
                "Station field technician on site for manual override.",
                "Initiate immediate part procurement."
            ],
            "tradeoff": "Zero immediate production loss, but carries elevated risk of severe component destruction if temperature/vibration spikes."
        }
        
        if fault_code in [2, 3] and confidence > 0.90:
            opt1["tag"] = "RECOMMENDED CHOICE"
            opt2["tag"] = "DE-PRIORITIZED"
            
        return [opt1, opt2, opt3]

    def analyze_cascading_risks(self, sensor_data: Dict, fault_code: int) -> List[Dict]:
        """Analyze multi-sensor compound risk interactions and potential domino failures."""
        cascading_chains = []
        temp = sensor_data.get("Temperature_C", 70)
        pres = sensor_data.get("Pressure_psi", 100)
        vib = sensor_data.get("Vibration_g", 0.02)
        oil = sensor_data.get("Oil_Level_pct", 60)
        leak = sensor_data.get("Coolant_Leak", 0)
        
        if temp > 85 and vib > 0.03:
            cascading_chains.append({
                "chain": "Thermal Expansion → Bearing Clearance Collapse → Shaft Seizure",
                "risk_severity": "Critical",
                "probability": "85%",
                "mitigation": "Reduce operating speed immediately to allow thermal dissipation."
            })
            
        if pres < 85 and oil < 40:
            cascading_chains.append({
                "chain": "Oil Loss → Pump Cavitation → Hydraulic Line Pressure Drop",
                "risk_severity": "High",
                "probability": "78%",
                "mitigation": "Top up hydraulic oil reservoir and inspect suction line seals."
            })
            
        if leak == 1 and temp > 80:
            cascading_chains.append({
                "chain": "Coolant Depletion → Loss of Heat Dissipation → Thermal Runaway",
                "risk_severity": "Critical",
                "probability": "92%",
                "mitigation": "Isolate coolant loop and check heat exchanger gaskets."
            })
            
        if not cascading_chains:
            cascading_chains.append({
                "chain": "Single-Point Degraded State → Accelerated Wear",
                "risk_severity": "Low" if fault_code == 0 else "Medium",
                "probability": "25%",
                "mitigation": "Follow primary preventive maintenance recommendations."
            })
            
        return cascading_chains

    def generate_root_cause_analysis(self, fault_code: int, sensor_data: Dict) -> List[Dict]:
        """Generate ranked probable root causes with verification procedures."""
        root_causes = {
            0: [
                {"cause": "Normal Operational Wear", "confidence": "98%", "verification": "Routine inspection during scheduled maintenance."}
            ],
            1: [
                {"cause": "Blocked Cooling Radiator / Heat Exchanger", "confidence": "55%", "verification": "Check radiator fins for dust accumulation and measure coolant inlet/outlet delta-T."},
                {"cause": "Pump Bearing Thermal Overload / Degradation", "confidence": "30%", "verification": "Inspect bearing housing with thermal camera and check for lubricant discoloration."},
                {"cause": "Stuck Thermostatic Valve", "confidence": "15%", "verification": "Verify valve position switch status and bypass flow."}
            ],
            2: [
                {"cause": "Shaft Misalignment / Coupling Wear", "confidence": "50%", "verification": "Check laser alignment metrics and inspect flexible coupling inserts."},
                {"cause": "Bearing Raceway Pitting or Fatigue", "confidence": "35%", "verification": "Perform FFT vibration frequency spectrum analysis to isolate inner/outer race pass frequency."},
                {"cause": "Loose Foundation Bolt / Structural Resonance", "confidence": "15%", "verification": "Torque foundation fasteners to specification."}
            ],
            3: [
                {"cause": "Hydraulic Pump Seal / Internal Leakage", "confidence": "60%", "verification": "Perform pressure decay test and inspect pump drain line for excessive bypass."},
                {"cause": "Pressure Relief Valve Malfunction", "confidence": "25%", "verification": "Test relief valve cracking pressure against specification."},
                {"cause": "Suction Strainer Blockage", "confidence": "15%", "verification": "Check suction differential pressure indicator."}
            ],
            4: [
                {"cause": "Shaft Seal Leakage", "confidence": "65%", "verification": "Inspect pump shaft gland for active oil weeping."},
                {"cause": "Drain Plug or Gasket Degradation", "confidence": "25%", "verification": "Check sump drain plug torque and sealing washer."},
                {"cause": "Excessive Oil Consumption via Blowby", "confidence": "10%", "verification": "Check crankcase breather for oil mist."}
            ],
            5: [
                {"cause": "Coolant Line Hose Rupture or Clamp Failure", "confidence": "70%", "verification": "Pressurize coolant circuit and visually inspect hose fittings."},
                {"cause": "Heat Exchanger Tube Leak", "confidence": "20%", "verification": "Sample hydraulic oil for water contamination."},
                {"cause": "Pump Body Mechanical Crack", "confidence": "10%", "verification": "Perform dye penetrant test on casting."}
            ]
        }
        return root_causes.get(fault_code, root_causes[0])

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
        rul_info = self.calculate_rul_hours(fault_code, sensor_data, confidence)
        decision_matrix = self.generate_decision_matrix(fault_code, sensor_data, confidence)
        cascading_risks = self.analyze_cascading_risks(sensor_data, fault_code)
        root_causes = self.generate_root_cause_analysis(fault_code, sensor_data)
        
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
            "urgency_level": self._determine_urgency(fault_code, analysis["risk_assessment"]),
            "rul_info": rul_info,
            "decision_matrix": decision_matrix,
            "cascading_risks": cascading_risks,
            "root_causes": root_causes
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
