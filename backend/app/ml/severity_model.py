import numpy as np

def predict_severity(vitals):
    """
    Input: vitals dict
    Output: severity_score (0 to 1), severity_label
    """
    score = 0.0
    # Oxygen level
    if vitals["spo2"] < 85:
        score += 0.4
    elif vitals["spo2"] < 92:
        score += 0.2
    # Heart rate
    if vitals["heart_rate"] > 120:
        score += 0.2
    elif vitals["heart_rate"] > 100:
        score += 0.1
    # Blood pressure
    if vitals["systolic_bp"] > 160 or vitals["diastolic_bp"] > 100:
        score += 0.2
    # Respiration rate
    if vitals["respiration_rate"] > 30:
        score += 0.2
    # Clamp score
    score = min(score, 1.0)

    # Severity label
    if score >= 0.7:
        label = "Critical"
    elif score >= 0.4:
        label = "Moderate"
    else:
        label = "Stable"

    return score, label
