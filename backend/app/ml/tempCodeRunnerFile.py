import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle

# Synthetic training data
# Features: [spo2, heart_rate, systolic_bp, diastolic_bp, respiration_rate]
X = np.array([
    [98, 80, 120, 80, 16],   # Stable
    [95, 90, 130, 85, 18],
    [90, 110, 140, 90, 22],  # Moderate
    [88, 115, 150, 95, 24],
    [82, 130, 160, 100, 30], # Critical
    [78, 140, 170, 110, 35],
])

# Labels: 0 = Stable, 1 = Moderate, 2 = Critical
y = np.array([0, 0, 1, 1, 2, 2])

# Train model
model = LogisticRegression(multi_class="ovr", max_iter=200)
model.fit(X, y)

# Save model
with open("severity_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Logistic Regression model trained & saved")
