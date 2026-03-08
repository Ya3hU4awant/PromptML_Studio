import os
import shutil
import joblib


def generate_preview_html(features, task_type):
    input_fields_html = ""
    for feat in features:
        safe_id = feat.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        input_fields_html += f"""
        <div class="field">
            <label>{feat}</label>
            <input type="number" id="{safe_id}" placeholder="0.0" step="any" value="0">
        </div>"""

    task_badge_color = "#6c63ff" if task_type == "classification" else "#00b4d8"
    safe_features = [f.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_") for f in features]

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PromptML Deployed Model</title>
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
    .result.show {{ background: #1a3a2a; border: 1px solid #2ecc71; color: #2ecc71; display: block; }}
    .note {{ margin-top: 16px; font-size: 0.78rem; color: #555; text-align: center; }}
  </style>
</head>
<body>
  <div class="header">
    <h2>PromptML Deployed Model</h2>
    <span class="badge">{task_type}</span>
  </div>
  <p class="subtitle">Enter values below and click Predict to see a sample output.</p>
  <div class="grid">{input_fields_html}</div>
  <button class="btn" onclick="predict()">Predict</button>
  <div class="result" id="result"></div>
  <p class="note">This is a UI preview only. Real predictions run after you deploy the downloaded ZIP.</p>
<script>
  var taskType = "{task_type}";
  var safeFeatures = {safe_features};
  function predict() {{
    var res = document.getElementById('result');
    var mockVal = taskType === 'classification'
      ? 'Class A (confidence: 87%)'
      : (Math.random() * 500000 + 100000).toFixed(2);
    res.innerText = 'Prediction: ' + mockVal + ' (deploy the ZIP for real predictions)';
    res.className = 'result show';
  }}
</script>
</body>
</html>"""
    return html


def generate_website(output_dir="generated_website"):
    # Clean previous build to avoid stale files
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Load artifacts
    model    = joblib.load("artifacts/model.pkl")
    features = joblib.load("artifacts/features.pkl")
    task_type = joblib.load("artifacts/task_type.pkl")

    # Build input UI code for each feature
    input_lines = []
    for col in features:
        safe_col = col.replace("'", "\\'")
        input_lines.append(f"inputs['{safe_col}'] = st.number_input('{safe_col}', value=0.0)")
    input_code = "\n".join(input_lines)

    # Determine correct prediction label column for pycaret version
    pred_col = "prediction_label"

    app_code = f"""import streamlit as st
import pandas as pd
import joblib
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="PromptML Deployed App", page_icon="\U0001F680", layout="centered")

# Hide Streamlit branding
st.markdown(\"\"\"<style>
#MainMenu {{visibility:hidden;}}
footer {{visibility:hidden;}}
[data-testid="stToolbarActions"] {{display:none;}}
</style>\"\"\", unsafe_allow_html=True)

st.title("PromptML Deployed Model")
st.caption("Task type: {task_type}")

@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

try:
    model = load_model()
except Exception as e:
    st.error("Model loading failed: " + str(e))
    st.stop()

features = {features}
task_type = "{task_type}"

st.subheader("Enter Input Values")
inputs = {{}}
{input_code}


df = pd.DataFrame([inputs])

if st.button("Predict", type="primary"):
    try:
        result = model.predict(df)
        value = result[0] if hasattr(result, '__len__') else result
        if task_type == "regression":
            st.success("Predicted Value: " + str(round(float(value), 4)))
        else:
            st.success("Predicted Class: " + str(value))
    except Exception as e:
        st.error("Prediction failed: " + str(e))
        st.info("Make sure all input values are filled correctly.")
"""

    # Write app.py
    with open(os.path.join(output_dir, "app.py"), "w", encoding="utf-8") as f:
        f.write(app_code)

    # Copy model.pkl
    shutil.copy("artifacts/model.pkl", os.path.join(output_dir, "model.pkl"))

    # requirements.txt — compatible with Python 3.11, no conflicts
    requirements = """streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0,<1.6.0
joblib>=1.3.0
pycaret[models]==3.3.2
"""
    with open(os.path.join(output_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(requirements)

    # runtime.txt — pin Python 3.11, prevents Python 3.14 build failures
    with open(os.path.join(output_dir, "runtime.txt"), "w", encoding="utf-8") as f:
        f.write("python-3.11\n")

    # .python-version — checked by Streamlit Cloud BEFORE runtime.txt
    with open(os.path.join(output_dir, ".python-version"), "w", encoding="utf-8") as f:
        f.write("3.11\n")

    # README.md — deploy instructions for user
    readme = """# PromptML Deployed Model

## Deploy to Streamlit Cloud (Free)

1. Create a new GitHub repository
2. Upload ALL files from this ZIP (including .python-version)
3. Go to https://share.streamlit.io
4. Connect your repo, select app.py
5. IMPORTANT: Before clicking Deploy, go to Advanced Settings
   and set Python version to 3.11
6. Click Deploy

## If you see: "No module named pycaret"
This means Python version was not set to 3.11.
Go to your app on share.streamlit.io, click the 3 dots menu,
select Settings, go to Advanced, set Python to 3.11,
then Reboot the app.

## Run Locally

pip install -r requirements.txt
streamlit run app.py

## Notes
- Python 3.11 is required - do NOT use Python 3.12, 3.13 or 3.14
- Do not change requirements.txt versions

Generated by PromptML Studio
"""
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    # ZIP everything
    zip_path = shutil.make_archive(output_dir, "zip", output_dir)

    return zip_path