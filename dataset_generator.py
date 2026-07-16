import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Number of samples
num_samples = 1000

# Initialize sensor value arrays
temperature = np.zeros(num_samples)
pressure = np.zeros(num_samples)
vibration = np.zeros(num_samples)
flow_rate = np.zeros(num_samples)
oil_level = np.zeros(num_samples)
rpm = np.zeros(num_samples)
coolant_leak = np.zeros(num_samples, dtype=int)
fault = []

# Generate each sample
for i in range(num_samples):
    # 1. Generate base normal values with noise
    temp_base = np.random.normal(70, 5)
    press_base = np.random.normal(100, 10)
    vib_base = np.random.normal(0.02, 0.005)
    flow_base = np.random.normal(300, 30)
    oil_base = np.random.normal(60, 10)
    rpm_base = np.random.normal(1500, 150)
    
    # 2. Clip to realistic physical boundaries, but allow natural overlap across classes
    temp_normal = np.clip(temp_base, 45.0, 95.0)
    press_normal = np.clip(press_base, 75.0, 140.0)
    vib_normal = np.clip(vib_base, 0.001, 0.05)
    flow_normal = np.clip(flow_base, 150.0, 450.0)
    oil_normal = np.clip(oil_base, 15.0, 100.0)
    rpm_normal = np.clip(rpm_base, 800.0, 2200.0)
    
    # Set default sensor values to the normal baseline
    temperature[i] = temp_normal
    pressure[i] = press_normal
    vibration[i] = vib_normal
    flow_rate[i] = flow_normal
    oil_level[i] = oil_normal
    rpm[i] = rpm_normal
    coolant_leak[i] = 0

    # 3. Assign scenario (fault type) and modify target sensors with overlapping/borderline boundaries
    scenario = np.random.randint(0, 6)

    # We will introduce a borderline case ratio (15%) to inject noisy, borderline values
    is_borderline = np.random.random() < 0.15

    # Normal
    if scenario == 0:
        if is_borderline:
            # Inject a single borderline sensor value (high temperature, high vibration, low pressure, or low oil)
            borderline_type = np.random.randint(0, 4)
            if borderline_type == 0:
                # Borderline elevated temperature (e.g. 85.0 to 91.0)
                temperature[i] = np.random.uniform(85.0, 91.0)
            elif borderline_type == 1:
                # Borderline elevated vibration (e.g. 0.035 to 0.043)
                vibration[i] = np.random.uniform(0.035, 0.043)
            elif borderline_type == 2:
                # Borderline low pressure (e.g. 76.0 to 83.0)
                pressure[i] = np.random.uniform(76.0, 83.0)
            else:
                # Borderline low oil (e.g. 27.0 to 34.0)
                oil_level[i] = np.random.uniform(27.0, 34.0)
        fault.append(0)

    # Overheating
    elif scenario == 1:
        if is_borderline:
            # Borderline overheating temp (overlaps with normal range)
            temperature[i] = np.clip(np.random.normal(86, 2), 83.0, 88.0)
        else:
            temperature[i] = np.clip(np.random.normal(95, 4), 88.0, 110.0)
        fault.append(1)

    # High vibration
    elif scenario == 2:
        if is_borderline:
            # Borderline high vibration (overlaps with normal range)
            vibration[i] = np.clip(np.random.normal(0.036, 0.002), 0.033, 0.039)
        else:
            vibration[i] = np.clip(np.random.normal(0.05, 0.005), 0.039, 0.08)
        fault.append(2)

    # Pressure failure
    elif scenario == 3:
        if is_borderline:
            # Borderline pressure failure (overlaps with normal range)
            pressure[i] = np.clip(np.random.normal(82, 2), 79.0, 85.0)
        else:
            pressure[i] = np.clip(np.random.normal(70, 5), 50.0, 79.0)
        fault.append(3)

    # Low oil
    elif scenario == 4:
        if is_borderline:
            # Borderline low oil (overlaps with normal range)
            oil_level[i] = np.clip(np.random.normal(32, 2), 29.0, 35.0)
        else:
            oil_level[i] = np.clip(np.random.normal(20, 5), 5.0, 29.0)
        fault.append(4)

    # Coolant leakage
    else:
        # Coolant leak occurs. We add sensor failure rate where the sensor reads 0
        if is_borderline:
            coolant_leak[i] = 0
            # A physical leak would also cause some temperature rise
            temperature[i] = np.clip(np.random.normal(83, 3), 78.0, 88.0)
        else:
            coolant_leak[i] = 1
        fault.append(5)

# Create dataset table
data = {
    "Temperature_C": temperature,
    "Pressure_psi": pressure,
    "Vibration_g": np.clip(vibration, 0, None),
    "Flow_Rate_lpm": flow_rate,
    "Oil_Level_pct": oil_level,
    "RPM": rpm,
    "Coolant_Leak": coolant_leak,
    "Fault": fault
}

# Convert to dataframe
df = pd.DataFrame(data)

# Save CSV and Excel files
df.to_csv("predictive_maintenance_dataset.csv", index=False)
try:
    df.to_excel("predictive_maintenance_dataset.xlsx", index=False)
except Exception as e:
    print(f"Note: Could not save Excel version: {e}")

print("Dataset Generated Successfully")