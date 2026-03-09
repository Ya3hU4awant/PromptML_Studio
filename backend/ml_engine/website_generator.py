import os
import shutil
import joblib
from datetime import datetime


def generate_preview_html(features, task_type):
    input_fields_html = ""
    for feat in features:
        input_fields_html += f"""
        <div class="field">
            <label>{feat}</label>
            <input type="number" id="{feat}" placeholder="0.0" step="any" value="0">
        </div>"""

    task_badge_color = "#6c63ff" if task_type == "classification" else "#00b4d8"

    html = f"""
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; padding: 24px; }}
  .header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }}
  .header h2 {{ font-size: 1.4rem; color: #ffffff; }}
  .badge {{ background: {task_badge_color}; color: white; font-size: 0.75rem; padding: 3px 10px; border-radius: 20px; font-weight: 600; text-transform: uppercase; }}
  .subtitle {{ color: #888; font-size: 0.9rem; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; margin-bottom: 24px; }}
  .field label {{ display: block; font-size: 0.78rem; color: #aaa; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .field input {{ width: 100%; padding: 9px 12px; background: #1e1e2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 0.95rem; outline: none; transition: border 0.2s; }}
  .field input:focus {{ border-color: {task_badge_color}; }}
  .btn {{ width: 100%; padding: 12px; background: linear-gradient(135deg, #6c63ff, #00b4d8); color: white; font-size: 1rem; font-weight: 600; border: none; border-radius: 10px; cursor: pointer; transition: opacity 0.2s; }}
  .btn:hover {{ opacity: 0.88; }}
  .result {{ margin-top: 18px; padding: 14px 18px; border-radius: 10px; font-size: 1rem; font-weight: 600; display: none; }}
  .result.success {{ background: #1a3a2a; border: 1px solid #2ecc71; color: #2ecc71; display: block; }}
  .note {{ margin-top: 16px; font-size: 0.78rem; color: #555; text-align: center; }}
</style>
</head>
<body>
  <div class="header">
    <h2>🚀 PromptML Deployed Model</h2>
    <span class="badge">{task_type}</span>
  </div>
  <p class="subtitle">Enter values below and click Predict to see a sample output.</p>
  <div class="grid">{input_fields_html}</div>
  <button class="btn" onclick="predict()">🔮 Predict</button>
  <div class="result success" id="result"></div>
  <p class="note">⚠️ This is a UI preview only. Real predictions run after you deploy the downloaded ZIP.</p>
<script>
  const task_type = "{task_type}";
  function predict() {{
    const fields = {list(features)};
    const res = document.getElementById('result');
    const mockVal = task_type === 'classification'
      ? 'Class A  (confidence: 87%)'
      : (Math.random() * 500000 + 100000).toFixed(2);
    res.innerText = '✅ Prediction: ' + mockVal + '   (deploy the ZIP for real predictions)';
  }}
</script>
</body></html>"""
    return html




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
