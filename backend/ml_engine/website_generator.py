import os
import shutil
import joblib

def generate_website(output_dir, task_type, target_column, model):
    # 🔴 DELETE OLD WEBSITE FIRST (VERY IMPORTANT)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    # 1️⃣ Streamlit app code
    app_code = f"""
import streamlit as st
import joblib

st.set_page_config(page_title="My ML Website")

st.title("My Generated ML App")

model = joblib.load("model.pkl")

value = st.number_input("Enter input value")

if st.button("Predict"):
    prediction = model.predict([[value]])
    st.success(f"Prediction: {{prediction}}")
"""

    # 2️⃣ Save app.py
    with open(os.path.join(output_dir, "app.py"), "w") as f:
        f.write(app_code)

    # 3️⃣ Save ONLY ONE model.pkl (in root)
    joblib.dump(model, os.path.join(output_dir, "model.pkl"))

    # 4️⃣ ZIP the folder
    zip_path = shutil.make_archive(
        base_name=output_dir,
        format="zip",
        root_dir=output_dir
    )

    return zip_path
