import pickle
import numpy as np
import os

model_path = os.path.join(os.path.dirname(__file__), "severity_model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

def predict_severity_ml(vitals):
    X = np.array([[
        vitals["spo2"],
        vitals["heart_rate"],
        vitals["systolic_bp"],
        vitals["diastolic_bp"],
        vitals["respiration_rate"]
    ]])

    probs = model.predict_proba(X)[0]
    class_id = probs.argmax()
    confidence = probs[class_id]

    if class_id == 0:
        label = "Stable"
    elif class_id == 1:
        label = "Moderate"
    else:
        label = "Critical"

    return float(confidence), label
