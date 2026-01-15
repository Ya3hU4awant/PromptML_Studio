import os
import shutil
import joblib

def generate_website(output_dir, task_type, target_column, model):
    # 1️⃣ output folder banao
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2️⃣ Simple Streamlit app code
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

    # 3️⃣ app.py save karo
    with open(os.path.join(output_dir, "app.py"), "w") as f:
        f.write(app_code)

    # 4️⃣ model save karo
    joblib.dump(model, os.path.join(output_dir, "model.pkl"))

    # 5️⃣ ZIP banao
    zip_path = shutil.make_archive(
        base_name=output_dir,
        format="zip",
        root_dir=output_dir
    )

    # 6️⃣ RETURN ZIP PATH (🔥 MOST IMPORTANT)
    return zip_path
