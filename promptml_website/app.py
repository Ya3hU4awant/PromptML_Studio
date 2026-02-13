
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
    st.error(f"❌ Model loading failed: {str(e)}")
    st.stop()

features = ['Id', 'SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'Species']
task_type = "regression"

st.subheader("🔢 Enter Input Values")

def user_inputs():
    data = {}
    for col in features:
        data[col] = st.number_input(col, value=0.0)
    return pd.DataFrame([data])

df = user_inputs()

if st.button("Predict"):
    try:
        pred = model.predict(df)
        st.success(f"Prediction: {pred[0]}")
    except:
        try:
            if task_type == "classification":
                from pycaret.classification import predict_model
                preds = predict_model(model, data=df)
                st.success(f"Prediction: {preds['prediction_label'].iloc[0]}")
            else:
                from pycaret.regression import predict_model
                preds = predict_model(model, data=df)
                st.success(f"Prediction: {preds['Label'].iloc[0]}")
        except Exception as e:
            st.error(f"Prediction failed: {e}")
st.info("ℹ️ If you face errors, run: pip install -r requirements.txt")

