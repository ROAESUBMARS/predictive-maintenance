import math
import random
import time

class SensorEngine:
    def __init__(self):
        self.tick_count = 0
        # Baselines for 12 Pumps
        self.pumps = {
            f"HP-{i:02d}": {
                "temp": 74.0 + random.uniform(-3, 3),
                "pres": 102.0 + random.uniform(-3, 3),
                "vib": 0.022 + random.uniform(-0.003, 0.003),
                "flow": 300.0 + random.uniform(-5, 5),
                "oil": 68.0 + random.uniform(-5, 5),
                "rpm": 1500.0 + random.uniform(-10, 10),
                "leak": 0,
                "status": "green",
                "fault": "Normal"
            } for i in range(1, 13)
        }
        
        # Inject known baseline state for HP-01 & HP-03 for initial realism
        self.pumps["HP-01"]["status"] = "red"
        self.pumps["HP-01"]["fault"] = "Overheating Detected"
        self.pumps["HP-01"]["temp"] = 94.5
        
        self.pumps["HP-03"]["status"] = "yellow"
        self.pumps["HP-03"]["fault"] = "High Vibration"
        self.pumps["HP-03"]["vib"] = 0.043

    def tick(self):
        self.tick_count += 1
        t = self.tick_count * 0.45
        updated_readings = {}

        for pump_id, p in self.pumps.items():
            # Sinusoidal micro-fluctuations (sensor noise)
            temp_val = p["temp"] + math.sin(t * 0.3) * 0.5 + random.uniform(-0.2, 0.2)
            pres_val = p["pres"] + math.cos(t * 0.4) * 0.8 + random.uniform(-0.3, 0.3)
            vib_val  = p["vib"]  + math.sin(t) * 0.0015 + random.uniform(-0.0005, 0.0005)
            flow_val = p["flow"] + math.cos(t * 0.8) * 2.5 + random.uniform(-1.0, 1.0)
            oil_val  = p["oil"]  + math.sin(t * 0.5) * 0.3 + random.uniform(-0.1, 0.1)
            rpm_val  = p["rpm"]  + math.sin(t * 0.6) * 8.0 + random.uniform(-3.0, 3.0)

            # Determine fault status dynamically based on threshold
            status = "green"
            fault = "Normal"
            if temp_val > 90.0:
                status = "red"
                fault = "Overheating Detected"
            elif vib_val > 0.038:
                status = "yellow" if vib_val < 0.050 else "red"
                fault = "High Vibration"
            elif pres_val < 75.0:
                status = "red"
                fault = "Pressure Failure"
            elif oil_val < 30.0:
                status = "yellow"
                fault = "Low Oil Level"

            updated_readings[pump_id] = {
                "pump_id": pump_id,
                "temp": round(temp_val, 1),
                "pressure": round(pres_val, 1),
                "vibration": round(vib_val, 4),
                "flow": round(flow_val, 0),
                "oil": round(oil_val, 0),
                "rpm": round(rpm_val, 0),
                "leak": p["leak"],
                "status": status,
                "fault": fault,
                "timestamp": int(time.time() * 1000)
            }

        return updated_readings

sensor_engine = SensorEngine()
