import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load dataset
df = pd.read_csv("predictive_maintenance_dataset.csv")

# Features and target
X = df.drop(columns=["Fault"])
y = df["Fault"]

# Define stratified K-fold cross-validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Instantiate classifier
model = RandomForestClassifier(random_state=42)

print("Performing Stratified 5-Fold Cross-Validation...")
cv_scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
print(f"Cross-Validation Accuracies: {cv_scores}")
print(f"Mean CV Accuracy: {np.mean(cv_scores):.4f} (std: {np.std(cv_scores):.4f})\n")

# Split data with stratification to maintain class balance in test set
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# Train AI model on training partition
print("Training model on stratified training set...")
model.fit(X_train, y_train)

# Predictions on held-out test partition
predictions = model.predict(X_test)

# Report evaluation metrics
print("\n=== Classification Report ===")
target_names = [
    "Normal (0)", 
    "Overheating (1)", 
    "High Vibration (2)", 
    "Pressure Failure (3)", 
    "Low Oil (4)", 
    "Coolant Leakage (5)"
]
print(classification_report(y_test, predictions, target_names=target_names))

print("=== Confusion Matrix ===")
cm = confusion_matrix(y_test, predictions)
cm_df = pd.DataFrame(cm, index=target_names, columns=[f"Pred {name}" for name in target_names])
print(cm_df)

# Save the trained model
joblib.dump(model, "saved_model.pkl")
print("\nAI Model Saved Successfully to saved_model.pkl")