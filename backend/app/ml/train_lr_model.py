import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle
import os

# Training data (synthetic)
X = np.array([
    [98, 80, 120, 80, 16],   # Stable
    [95, 90, 130, 85, 18],
    [90, 110, 140, 90, 22],  # Moderate
    [88, 115, 150, 95, 24],
    [82, 130, 160, 100, 30], # Critical
    [78, 140, 170, 110, 35],
])

# Labels: 0=Stable, 1=Moderate, 2=Critical
y = np.array([0, 0, 1, 1, 2, 2])

model = LogisticRegression(multi_class="ovr", max_iter=500)
model.fit(X, y)

# SAVE MODEL IN SAME FOLDER
model_path = os.path.join(os.path.dirname(__file__), "severity_model.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print("✅ ML model trained & saved at:", model_path)
