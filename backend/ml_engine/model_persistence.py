import os
import joblib

ARTIFACTS_DIR = "artifacts"

def save_artifacts(model, feature_columns, task_type):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    joblib.dump(model, os.path.join(ARTIFACTS_DIR, "model.pkl"))
    joblib.dump(feature_columns, os.path.join(ARTIFACTS_DIR, "features.pkl"))
    joblib.dump(task_type, os.path.join(ARTIFACTS_DIR, "task_type.pkl"))
