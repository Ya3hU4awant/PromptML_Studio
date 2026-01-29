import os
import shutil
import joblib
from datetime import datetime

def generate_website(output_dir="generated_website"):
    os.makedirs(output_dir, exist_ok=True)

    # Load artifacts
    model = joblib.load("artifacts/model.pkl")
    features = joblib.load("artifacts/features.pkl")
    task_type = joblib.load("artifacts/task_type.pkl")

    # Streamlit app template (AUTO UI)
    app_code = f"""
import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="PromptML Deployed App")

st.title("🚀 PromptML Deployed Model")

try:
    model = joblib.load("model.pkl")
except ModuleNotFoundError:
    st.error("❌ PyCaret is missing. Install dependencies from requirements.txt")
    st.stop()
except Exception as e:
    st.error(f"❌ Model loading failed: {{str(e)}}")
    st.stop()

features = {features}
task_type = "{task_type}"

st.subheader("🔢 Enter Input Values")

def user_inputs():
    data = {{}}
    for col in features:
        data[col] = st.number_input(col, value=0.0)
    return pd.DataFrame([data])

df = user_inputs()

if st.button("Predict"):
    try:
        pred = model.predict(df)
        st.success(f"Prediction: {{pred[0]}}")
    except:
        try:
            if task_type == "classification":
                from pycaret.classification import predict_model
                preds = predict_model(model, data=df)
                st.success(f"Prediction: {{preds['prediction_label'].iloc[0]}}")
            else:
                from pycaret.regression import predict_model
                preds = predict_model(model, data=df)
                st.success(f"Prediction: {{preds['Label'].iloc[0]}}")
        except Exception as e:
            st.error(f"Prediction failed: {{e}}")
st.info("ℹ️ If you face errors, run: pip install -r requirements.txt")

"""


    # Write app.py
    with open(os.path.join(output_dir, "app.py"), "w", encoding="utf-8") as f:
        f.write(app_code)


    # Copy model.pkl
    shutil.copy("artifacts/model.pkl", os.path.join(output_dir, "model.pkl"))

    # Create requirements.txt
    requirements =  """streamlit
pandas
numpy
scikit-learn
joblib
pycaret==3.1.0
"""

    with open(os.path.join(output_dir, "requirements.txt"), "w") as f:
        f.write(requirements)

    # ZIP everything
    zip_path = shutil.make_archive(output_dir, "zip", output_dir)

    return zip_path
