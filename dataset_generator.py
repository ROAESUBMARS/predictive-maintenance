import pandas as pd
import numpy as np

# Number of samples
num_samples = 1000

# Generate sensor values
temperature = np.random.normal(70, 10, num_samples)
pressure = np.random.normal(100, 15, num_samples)
vibration = np.random.normal(0.02, 0.01, num_samples)
flow_rate = np.random.normal(300, 50, num_samples)
oil_level = np.random.normal(60, 15, num_samples)
rpm = np.random.normal(1500, 200, num_samples)
coolant_leak = np.random.choice([0, 1], num_samples)

# Create fault types
fault = []

# Assign a scenario (fault type) for each sample and modify sensor values accordingly
for i in range(num_samples):

    scenario = np.random.randint(0, 6)

    # Normal
    if scenario == 0:
        temperature[i] = 70
        pressure[i] = 100
        vibration[i] = 0.02
        oil_level[i] = 60
        coolant_leak[i] = 0
        fault.append(0)

    # Overheating
    elif scenario == 1:
        temperature[i] = 95
        fault.append(1)

    # High vibration
    elif scenario == 2:
        vibration[i] = 0.05
        fault.append(2)

    # Pressure failure
    elif scenario == 3:
        pressure[i] = 70
        fault.append(3)

    # Low oil
    elif scenario == 4:
        oil_level[i] = 20
        fault.append(4)

    # Coolant leakage
    else:
        coolant_leak[i] = 1
        fault.append(5)
        
        # Create dataset table
data = {
    "Temperature_C": temperature,
    "Pressure_psi": pressure,
    "Vibration_g": vibration,
    "Flow_Rate_lpm": flow_rate,
    "Oil_Level_pct": oil_level,
    "RPM": rpm,
    "Coolant_Leak": coolant_leak,
    "Fault": fault
}

# Convert to dataframe
df = pd.DataFrame(data)

# Save CSV
df.to_csv("predictive_maintenance_dataset.csv", index=False)

print("Dataset Generated Successfully")