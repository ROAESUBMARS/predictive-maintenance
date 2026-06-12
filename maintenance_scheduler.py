"""
Maintenance Scheduler for Predictive Maintenance System
Manages maintenance schedules, tracks service history, and optimizes maintenance intervals
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


class MaintenanceScheduler:
    """
    Intelligent maintenance scheduling system that optimizes maintenance intervals
    based on fault predictions, sensor data, and equipment history.
    """

    def __init__(self):
        """Initialize the maintenance scheduler with default intervals and policies."""
        self.maintenance_intervals = self._initialize_intervals()
        self.service_history = []
        self.upcoming_schedule = []
        self.maintenance_policies = self._initialize_policies()

    @staticmethod
    def _initialize_intervals() -> Dict:
        """Define standard maintenance intervals based on fault severity."""
        return {
            "routine": {
                "interval_days": 7,
                "severity": "low",
                "description": "Regular monitoring and data collection",
                "tasks": ["Check all sensor readings", "Verify data logging", "Visual inspection"]
            },
            "preventive": {
                "interval_days": 14,
                "severity": "medium",
                "description": "Preventive maintenance to avoid failures",
                "tasks": ["Clean cooling system", "Check fluid levels", "Inspect bearings", "Lubricate moving parts"]
            },
            "corrective": {
                "interval_days": 1,
                "severity": "high",
                "description": "Immediate repair of detected faults",
                "tasks": ["Diagnose fault", "Replace defective parts", "Test system", "Document changes"]
            },
            "urgent": {
                "interval_days": 0.5,
                "severity": "critical",
                "description": "Emergency maintenance for critical faults",
                "tasks": ["Stop system if unsafe", "Emergency repairs", "Continuous monitoring", "Full system test"]
            }
        }

    @staticmethod
    def _initialize_policies() -> Dict:
        """Define maintenance policies and strategies."""
        return {
            "condition_based": {
                "name": "Condition-Based Maintenance",
                "description": "Schedule based on actual equipment condition",
                "advantages": ["Optimal intervals", "Cost-effective", "Reduced downtime"],
                "implementation": "Uses sensor data to determine maintenance timing"
            },
            "predictive": {
                "name": "Predictive Maintenance",
                "description": "Predict failures before they occur",
                "advantages": ["Prevents failures", "Maximizes uptime", "Reduces emergency repairs"],
                "implementation": "Uses AI model predictions to schedule maintenance"
            },
            "time_based": {
                "name": "Time-Based Maintenance",
                "description": "Fixed intervals regardless of condition",
                "advantages": ["Simple planning", "Consistent intervals"],
                "implementation": "Every X days/hours regardless of system state"
            }
        }

    def schedule_next_maintenance(self, fault_code: int, confidence: float, 
                                  operating_hours: float, current_date: datetime = None) -> Dict:
        """
        Calculate the next maintenance schedule based on fault prediction.

        Args:
            fault_code: Current fault classification (0-5)
            confidence: Model confidence level (0-1)
            operating_hours: Total equipment operating hours
            current_date: Reference date (defaults to today)

        Returns:
            Dictionary with next maintenance details
        """
        if current_date is None:
            current_date = datetime.now()

        maintenance_type = self._determine_maintenance_type(fault_code, confidence)
        interval_days = self.maintenance_intervals[maintenance_type]["interval_days"]
        
        next_scheduled_date = current_date + timedelta(days=interval_days)
        
        schedule = {
            "current_date": current_date.strftime("%Y-%m-%d %H:%M:%S"),
            "maintenance_type": maintenance_type,
            "severity": self.maintenance_intervals[maintenance_type]["severity"],
            "next_scheduled_date": next_scheduled_date.strftime("%Y-%m-%d"),
            "days_until_maintenance": int((next_scheduled_date - current_date).days),
            "description": self.maintenance_intervals[maintenance_type]["description"],
            "tasks": self.maintenance_intervals[maintenance_type]["tasks"],
            "estimated_duration_hours": self._estimate_duration(maintenance_type),
            "estimated_cost": self._estimate_cost(maintenance_type),
            "required_staff": self._get_required_staff(maintenance_type),
            "spare_parts": self._get_spare_parts_list(fault_code),
            "tools_needed": self._get_tools_needed(fault_code),
            "priority": self._calculate_priority(fault_code, confidence),
            "impact_if_delayed": self._assess_delay_impact(fault_code),
            "confidence_score": confidence,
            "recommended_action": self._get_recommended_action(fault_code, confidence)
        }
        
        return schedule

    def generate_monthly_schedule(self, equipment_data: List[Dict], 
                                 current_date: datetime = None) -> Dict:
        """
        Generate a month-long maintenance schedule for multiple equipment.

        Args:
            equipment_data: List of equipment with fault codes and operating data
            current_date: Reference date (defaults to today)

        Returns:
            Dictionary with consolidated monthly schedule
        """
        if current_date is None:
            current_date = datetime.now()

        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        monthly_schedule = {
            "month": month_start.strftime("%B %Y"),
            "period": f"{month_start.strftime('%Y-%m-%d')} to {month_end.strftime('%Y-%m-%d')}",
            "schedule_items": [],
            "total_estimated_hours": 0,
            "total_estimated_cost": 0,
            "critical_items": [],
            "summary": {}
        }
        
        # Generate schedules for each equipment
        for equipment in equipment_data:
            schedule = self.schedule_next_maintenance(
                equipment.get("fault_code", 0),
                equipment.get("confidence", 0.85),
                equipment.get("operating_hours", 0),
                current_date
            )
            
            scheduled_date = datetime.strptime(schedule["next_scheduled_date"], "%Y-%m-%d")
            
            # Only include if scheduled within this month
            if month_start <= scheduled_date <= month_end:
                schedule_item = {
                    "equipment_id": equipment.get("id", "Unknown"),
                    "equipment_name": equipment.get("name", "Equipment"),
                    **schedule
                }
                monthly_schedule["schedule_items"].append(schedule_item)
                monthly_schedule["total_estimated_hours"] += schedule["estimated_duration_hours"]
                monthly_schedule["total_estimated_cost"] += schedule["estimated_cost"]
                
                if schedule["severity"] in ["critical", "high"]:
                    monthly_schedule["critical_items"].append({
                        "equipment": equipment.get("name", "Equipment"),
                        "date": schedule["next_scheduled_date"],
                        "priority": schedule["priority"]
                    })
        
        # Generate summary
        monthly_schedule["summary"] = self._generate_schedule_summary(monthly_schedule)
        
        return monthly_schedule

    def generate_annual_maintenance_plan(self, equipment_list: List[Dict]) -> Dict:
        """
        Generate a comprehensive annual maintenance plan.

        Args:
            equipment_list: List of all equipment to maintain

        Returns:
            Dictionary with annual maintenance plan
        """
        plan = {
            "year": datetime.now().year,
            "total_equipment": len(equipment_list),
            "quarterly_schedules": [],
            "maintenance_budget": {
                "q1": 0,
                "q2": 0,
                "q3": 0,
                "q4": 0,
                "total": 0
            },
            "resource_allocation": {
                "technicians_needed": 0,
                "peak_period": None,
                "average_monthly_hours": 0
            },
            "strategic_recommendations": []
        }
        
        current_date = datetime(datetime.now().year, 1, 1)
        
        # Generate quarterly schedules
        for quarter in range(1, 5):
            quarter_date = datetime(datetime.now().year, (quarter - 1) * 3 + 1, 1)
            monthly_schedules = []
            
            # Generate 3 months worth of schedules
            for month in range(3):
                month_date = quarter_date + timedelta(days=30 * month)
                monthly = self.generate_monthly_schedule(equipment_list, month_date)
                monthly_schedules.append(monthly)
                plan["maintenance_budget"][f"q{quarter}"] += monthly["total_estimated_cost"]
            
            plan["quarterly_schedules"].append({
                "quarter": f"Q{quarter}",
                "months": monthly_schedules,
                "total_hours": sum(m["total_estimated_hours"] for m in monthly_schedules),
                "total_cost": plan["maintenance_budget"][f"q{quarter}"]
            })
        
        plan["maintenance_budget"]["total"] = sum(
            plan["maintenance_budget"][f"q{i}"] for i in range(1, 5)
        )
        
        # Calculate resource needs
        total_hours = plan["maintenance_budget"]["total"]
        plan["resource_allocation"]["average_monthly_hours"] = total_hours / 12
        plan["resource_allocation"]["technicians_needed"] = max(1, int(plan["resource_allocation"]["average_monthly_hours"] / 160))
        
        # Generate strategic recommendations
        plan["strategic_recommendations"] = self._generate_strategic_recommendations(equipment_list)
        
        return plan

    @staticmethod
    def _determine_maintenance_type(fault_code: int, confidence: float) -> str:
        """Determine the type of maintenance needed."""
        if fault_code == 0:
            return "routine"
        elif fault_code in [1, 2, 3, 5]:  # Critical faults
            if confidence > 0.90:
                return "urgent"
            else:
                return "corrective"
        elif fault_code == 4:  # Warning fault
            return "preventive"
        else:
            return "routine"

    @staticmethod
    def _estimate_duration(maintenance_type: str) -> float:
        """Estimate maintenance duration in hours."""
        duration_map = {
            "routine": 1.0,
            "preventive": 3.0,
            "corrective": 6.0,
            "urgent": 4.0
        }
        return duration_map.get(maintenance_type, 2.0)

    @staticmethod
    def _estimate_cost(maintenance_type: str) -> float:
        """Estimate maintenance cost in dollars."""
        cost_map = {
            "routine": 50,
            "preventive": 300,
            "corrective": 800,
            "urgent": 1500
        }
        return cost_map.get(maintenance_type, 200)

    @staticmethod
    def _get_required_staff(maintenance_type: str) -> List[str]:
        """Get required staff for maintenance."""
        staff_map = {
            "routine": ["Technician"],
            "preventive": ["Senior Technician", "Assistant"],
            "corrective": ["Senior Technician", "Specialist", "Assistant"],
            "urgent": ["Lead Technician", "Specialist", "2x Assistants"]
        }
        return staff_map.get(maintenance_type, ["Technician"])

    @staticmethod
    def _get_spare_parts_list(fault_code: int) -> List[str]:
        """Get spare parts needed for specific fault."""
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
    def _get_tools_needed(fault_code: int) -> List[str]:
        """Get tools needed for maintenance."""
        tools_map = {
            0: ["Digital multimeter", "Pressure gauge", "Thermometer"],
            1: ["Wrench set", "Thermal imaging camera", "Coolant pressure tester"],
            2: ["Alignment tools", "Vibration analyzer", "Torque wrench"],
            3: ["Hydraulic jack", "Pressure gauge kit", "Hose crimper"],
            4: ["Oil pump", "Filter wrench", "Oil drain pan"],
            5: ["Pipe wrench", "Leak detection kit", "Coolant temperature gauge"]
        }
        return tools_map.get(fault_code, ["Basic tool kit"])

    @staticmethod
    def _calculate_priority(fault_code: int, confidence: float) -> int:
        """Calculate priority score (1-10, where 10 is highest)."""
        base_priority = {
            0: 1,
            1: 9,
            2: 9,
            3: 10,
            4: 4,
            5: 10
        }
        priority = base_priority.get(fault_code, 5)
        # Adjust based on confidence
        priority = int(priority * confidence)
        return min(10, max(1, priority))

    @staticmethod
    def _assess_delay_impact(fault_code: int) -> Dict:
        """Assess impact of delaying maintenance."""
        impact_map = {
            0: {
                "risk_level": "None",
                "potential_consequences": "None",
                "failure_probability": 0.0
            },
            1: {
                "risk_level": "High",
                "potential_consequences": "System overheating, component damage, potential fire hazard",
                "failure_probability": 0.85
            },
            2: {
                "risk_level": "High",
                "potential_consequences": "Equipment breakage, catastrophic failure, safety hazard",
                "failure_probability": 0.90
            },
            3: {
                "risk_level": "Critical",
                "potential_consequences": "Complete system failure, potential injury hazard",
                "failure_probability": 0.95
            },
            4: {
                "risk_level": "Medium",
                "potential_consequences": "Continued oil loss, eventual component failure",
                "failure_probability": 0.65
            },
            5: {
                "risk_level": "Critical",
                "potential_consequences": "Coolant loss, overheating, system damage",
                "failure_probability": 0.92
            }
        }
        return impact_map.get(fault_code, {"risk_level": "Unknown", "potential_consequences": "Unknown", "failure_probability": 0.5})

    @staticmethod
    def _get_recommended_action(fault_code: int, confidence: float) -> str:
        """Get recommended action based on fault and confidence."""
        if fault_code == 0:
            return "Continue standard maintenance schedule"
        elif fault_code in [1, 3, 5]:
            if confidence > 0.90:
                return "URGENT: Schedule maintenance within 24 hours"
            else:
                return "Schedule maintenance within 48-72 hours"
        elif fault_code == 2:
            if confidence > 0.90:
                return "URGENT: Schedule maintenance within 12 hours"
            else:
                return "Schedule maintenance within 24-48 hours"
        elif fault_code == 4:
            return "Schedule maintenance within 2-3 days"
        else:
            return "Monitor and schedule as needed"

    @staticmethod
    def _generate_schedule_summary(monthly_schedule: Dict) -> Dict:
        """Generate summary statistics for monthly schedule."""
        schedule_items = monthly_schedule["schedule_items"]
        
        severity_counts = {
            "critical": len([s for s in schedule_items if s["severity"] == "critical"]),
            "high": len([s for s in schedule_items if s["severity"] == "high"]),
            "medium": len([s for s in schedule_items if s["severity"] == "medium"]),
            "low": len([s for s in schedule_items if s["severity"] == "low"])
        }
        
        return {
            "total_scheduled_items": len(schedule_items),
            "severity_breakdown": severity_counts,
            "total_estimated_hours": monthly_schedule["total_estimated_hours"],
            "total_estimated_cost": monthly_schedule["total_estimated_cost"],
            "critical_items_count": len(monthly_schedule["critical_items"]),
            "average_task_duration_hours": (
                monthly_schedule["total_estimated_hours"] / len(schedule_items) 
                if schedule_items else 0
            )
        }

    @staticmethod
    def _generate_strategic_recommendations(equipment_list: List[Dict]) -> List[str]:
        """Generate strategic maintenance recommendations."""
        recommendations = []
        
        # Analyze fault patterns
        fault_counts = {}
        for equipment in equipment_list:
            fault = equipment.get("fault_code", 0)
            fault_counts[fault] = fault_counts.get(fault, 0) + 1
        
        # Generate recommendations based on patterns
        if fault_counts.get(1, 0) > len(equipment_list) * 0.3:
            recommendations.append("High frequency of overheating faults - Consider upgrade to cooling system")
        
        if fault_counts.get(2, 0) > len(equipment_list) * 0.3:
            recommendations.append("High frequency of vibration faults - Review bearing maintenance intervals")
        
        if fault_counts.get(5, 0) > len(equipment_list) * 0.3:
            recommendations.append("High frequency of coolant leaks - Inspect seals and connections")
        
        recommendations.append("Implement predictive maintenance for early fault detection")
        recommendations.append("Maintain spare parts inventory for critical components")
        recommendations.append("Schedule staff training for equipment maintenance")
        
        return recommendations

    def export_schedule_json(self, schedule: Dict) -> str:
        """Export schedule as JSON."""
        return json.dumps(schedule, indent=2, default=str)

    def export_schedule_report(self, schedule: Dict) -> str:
        """Export schedule as formatted text report."""
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║              MAINTENANCE SCHEDULE REPORT                       ║
╚════════════════════════════════════════════════════════════════╝

MAINTENANCE TIMING
─────────────────────────────────────────────────────────────────
Current Date:              {schedule['current_date']}
Next Scheduled Date:       {schedule['next_scheduled_date']}
Days Until Maintenance:    {schedule['days_until_maintenance']}
Maintenance Type:          {schedule['maintenance_type'].upper()}
Priority Level:            {schedule['priority']}/10
Severity:                  {schedule['severity'].upper()}

MAINTENANCE DETAILS
─────────────────────────────────────────────────────────────────
Description: {schedule['description']}

Tasks to Perform:
"""
        for i, task in enumerate(schedule['tasks'], 1):
            report += f"  {i}. {task}\n"

        report += f"""
RESOURCE REQUIREMENTS
─────────────────────────────────────────────────────────────────
Estimated Duration:  {schedule['estimated_duration_hours']} hours
Estimated Cost:      ${schedule['estimated_cost']}
Required Staff:      {', '.join(schedule['required_staff'])}

Spare Parts Needed:
"""
        if schedule['spare_parts']:
            for part in schedule['spare_parts']:
                report += f"  • {part}\n"
        else:
            report += "  • None\n"

        report += f"""
Tools Needed:
"""
        for tool in schedule['tools_needed']:
            report += f"  • {tool}\n"

        report += f"""
RISK ASSESSMENT
─────────────────────────────────────────────────────────────────
Impact if Delayed:      {schedule['impact_if_delayed']['risk_level']}
Failure Probability:    {schedule['impact_if_delayed']['failure_probability']:.0%}
Consequences:           {schedule['impact_if_delayed']['potential_consequences']}

RECOMMENDATION
─────────────────────────────────────────────────────────────────
{schedule['recommended_action']}

═════════════════════════════════════════════════════════════════
"""
        return report


# Example usage
if __name__ == "__main__":
    scheduler = MaintenanceScheduler()
    
    # Example: Schedule next maintenance for a system with overheating
    print("SINGLE EQUIPMENT MAINTENANCE SCHEDULE")
    print("=" * 65)
    schedule = scheduler.schedule_next_maintenance(
        fault_code=1,
        confidence=0.92,
        operating_hours=2450
    )
    print(scheduler.export_schedule_report(schedule))
    
    # Example: Monthly schedule for multiple equipment
    print("\n\nMONTHLY MAINTENANCE SCHEDULE")
    print("=" * 65)
    equipment_data = [
        {"id": "EQP001", "name": "Pump A", "fault_code": 0, "confidence": 0.98, "operating_hours": 2400},
        {"id": "EQP002", "name": "Pump B", "fault_code": 1, "confidence": 0.92, "operating_hours": 2450},
        {"id": "EQP003", "name": "Compressor C", "fault_code": 4, "confidence": 0.80, "operating_hours": 1200},
        {"id": "EQP004", "name": "Motor D", "fault_code": 2, "confidence": 0.88, "operating_hours": 3100},
    ]
    
    monthly_schedule = scheduler.generate_monthly_schedule(equipment_data)
    print(json.dumps(monthly_schedule, indent=2, default=str))
    
    # Example: Annual maintenance plan
    print("\n\nANNUAL MAINTENANCE PLAN")
    print("=" * 65)
    annual_plan = scheduler.generate_annual_maintenance_plan(equipment_data)
    print(json.dumps(annual_plan, indent=2, default=str))
