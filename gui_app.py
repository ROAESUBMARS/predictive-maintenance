import tkinter as tk
from tkinter import messagebox
import pandas as pd
import joblib
import random

model = joblib.load("saved_model.pkl")
root = tk.Tk()
root.title("AI Predictive Maintenance System")
root.geometry("700x650")
root.configure(bg="#1e1e1e")
title = tk.Label(root, text="AI Predictive Maintenance Dashboard", font=("Arial", 22, "bold"), bg="#1e1e1e", fg="cyan")
title.pack(pady=20)
tk.Label(root, text="Temperature", bg="#1e1e1e", fg="white", font=("Arial", 11, "bold")).pack()
temperature_entry = tk.Entry(root)
temperature_entry.pack()
tk.Label(root, text="Pressure", bg="#1e1e1e", fg="white", font=("Arial", 11, "bold")).pack()
pressure_entry = tk.Entry(root)
pressure_entry.pack()
tk.Label(root, text="Vibration", bg="#1e1e1e", fg="white", font=("Arial", 11, "bold")).pack()
vibration_entry = tk.Entry(root)
vibration_entry.pack()
tk.Label(root, text="Flow Rate", bg="#1e1e1e", fg="white", font=("Arial", 11, "bold")).pack()
flow_entry = tk.Entry(root)
flow_entry.pack()
tk.Label(root, text="Oil Level", bg="#1e1e1e", fg="white", font=("Arial", 11, "bold")).pack()
oil_entry = tk.Entry(root)
oil_entry.pack()
tk.Label(root, text="RPM", bg="#1e1e1e", fg="white", font=("Arial", 11, "bold")).pack()
rpm_entry = tk.Entry(root)
rpm_entry.pack()
tk.Label(root, text="Coolant Leak (0 or 1)", bg="#1e1e1e", fg="white", font=("Arial", 11, "bold")).pack()
leak_entry = tk.Entry(root)
leak_entry.pack()
def predict_fault():
    try:
        temperature = float(temperature_entry.get())
        pressure = float(pressure_entry.get())
        vibration = float(vibration_entry.get())
        flow_rate = float(flow_entry.get())
        oil_level = float(oil_entry.get())
        rpm = float(rpm_entry.get())
        coolant_leak = int(leak_entry.get())
        data = pd.DataFrame([{
            "Temperature_C": temperature,
    "Pressure_psi": pressure,
    "Vibration_g": vibration,
    "Flow_Rate_lpm": flow_rate,
    "Oil_Level_pct": oil_level,
    "RPM": rpm,
    "Coolant_Leak": coolant_leak
}])

        prediction = model.predict(data)
        fault_info = {0: {"fault": "System Operating Normally", "recommendation": "No maintenance required"}, 1: {"fault": "Overheating Fault", "recommendation": "Check cooling system and inspect pump bearings"}, 2: {"fault": "High Vibration Fault", "recommendation": "Inspect rotating parts and tighten loose components"}, 3: {"fault": "Pressure Failure", "recommendation": "Check hydraulic pressure lines and pump condition"}, 4: {"fault": "Low Oil Level", "recommendation": "Refill oil and inspect for leakage"}, 5: {"fault": "Coolant Leakage Fault", "recommendation": "Inspect coolant pipes and repair leakage"}}
        result = fault_info[prediction[0]]
        result_color = "lime" if prediction[0] == 0 else "red"
        result_label.config(text=f"Fault: {result['fault']}\n\nRecommendation: {result['recommendation']}", fg=result_color)
    except Exception as e:
        messagebox.showerror("Error", f"Please enter valid values\n{e}")
        
    # Random fault scenario
    scenario = random.randint(0, 5)

    # Normal
    if scenario == 0:
        temperature = 70
        pressure = 100
        vibration = 0.02
        oil = 60
        leak = 0

    # Overheating
    elif scenario == 1:
        temperature = 95
        pressure = 120
        vibration = 0.02
        oil = 60
        leak = 0

    # High vibration
    elif scenario == 2:
        temperature = 70
        pressure = 100
        vibration = 0.05
        oil = 60
        leak = 0

    # Pressure failure
    elif scenario == 3:
        temperature = 70
        pressure = 70
        vibration = 0.02
        oil = 60
        leak = 0

    # Low oil
    elif scenario == 4:
        temperature = 70
        pressure = 100
        vibration = 0.02
        oil = 20
        leak = 0

    # Coolant leakage
    else:
        temperature = 70
        pressure = 100
        vibration = 0.02
        oil = 60
        leak = 1

    # Insert values
    temperature_entry.delete(0, tk.END)
    temperature_entry.insert(0, temperature)

    pressure_entry.delete(0, tk.END)
    pressure_entry.insert(0, pressure)

    vibration_entry.delete(0, tk.END)
    vibration_entry.insert(0, vibration)

    flow_entry.delete(0, tk.END)
    flow_entry.insert(0, 300)

    oil_entry.delete(0, tk.END)
    oil_entry.insert(0, oil)

    rpm_entry.delete(0, tk.END)
    rpm_entry.insert(0, 1500)

    leak_entry.delete(0, tk.END)
    leak_entry.insert(0, leak)

    hours_entry.delete(0, tk.END)
    hours_entry.insert(0, 100)

    # Run AI prediction
    predict_fault()


predict_button = tk.Button(root, text="RUN AI DIAGNOSIS", command=predict_fault, bg="cyan", fg="black", font=("Arial", 13, "bold"), width=25, height=2)
predict_button.pack(pady=25)
result_label = tk.Label(root, text="System Waiting for Analysis...", font=("Arial", 14, "bold"), bg="#1e1e1e", fg="lime", wraplength=600, justify="left")
result_label.pack(pady=20)

root.mainloop()
