"""
PromptML Studio - Main Streamlit Application
AI-Powered AutoML Platform with Dual-Mode Interface
"""
import requests

import streamlit as st
st.set_page_config(page_title="PromptML Studio", layout="wide")
import shutil
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys
import os
import io
import zipfile
import tempfile
from datetime import datetime
import warnings
import traceback
warnings.filterwarnings('ignore')

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from backend.ml_engine.prompt_parser import PromptParser
from backend.ml_engine.model_builder import ModelBuilder
from backend.ml_engine.report_generator import ReportGenerator
from backend.ml_engine.website_generator import generate_website
from backend.predictor import Predictor


# ---------- Web App Generator Helpers ----------

@st.cache_data
def infer_types(df):
    """Infer input types per feature column for UI generation."""
    types = {}
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            types[col] = 'numeric'
        elif df[col].dtype == 'object':
            types[col] = 'categorical'
        else:
            types[col] = 'text'
    return types


def generate_app_template(feature_columns, feature_types, sample_data=None):
    """Fixed template generation with real categorical options."""
    input_code = []
    cat_options = {}  # Store real options for categorical
    
    # If sample data available, extract real categorical options
    if sample_data is not None:
        for col in feature_columns:
            if feature_types.get(col) == 'categorical':
                unique_vals = sample_data[col].dropna().unique()[:10]  # Top 10 options
                cat_options[col] = [str(v) for v in unique_vals]
    
    for col in feature_columns:
        ftype = feature_types.get(col, 'numeric')
        if ftype == 'numeric':
            input_code.append(f"    {col} = st.number_input('{col}', value=0.0)")
        elif ftype == 'categorical':
            options = cat_options.get(col, ['Option1', 'Option2'])
            options_str = repr(options)
            input_code.append(f"    {col} = st.selectbox('{col}', {options_str})")
        else:
            input_code.append(f"    {col} = st.text_input('{col}')")
    
    input_code_str = "\n".join(input_code)
    feature_cols_literal = "', '".join(feature_columns)
    
    # FIXED: Correct dictionary syntax
    template = f'''import streamlit as st
import pandas as pd
import joblib
import numpy as np

@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

model = load_model()
feature_columns = {repr(feature_columns)}

st.title("🧠 ML Model Predictor")
st.markdown("Upload CSV or use form for predictions.")

# Batch prediction
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    missing = set(feature_columns) - set(df.columns)
    if missing:
        st.error(f"Missing columns: {{missing}}")
    else:
        try:
            predictions = model.predict(df[feature_columns])
        except:
            if TASK_TYPE == "classification":
                from pycaret.classification import predict_model
                preds = predict_model(model, data=df[feature_columns])
                predictions = preds['prediction_label']
            else:
                from pycaret.regression import predict_model
                preds = predict_model(model, data=df[feature_columns])
                predictions = preds['Label']

        st.write("Predictions:", predictions)
        st.download_button("Download CSV", pd.DataFrame({{'predictions': predictions}}).to_csv(index=False), "predictions.csv")
    st.stop()

# Single prediction - FIXED SYNTAX
st.header("🔮 Single Prediction")
def user_input_features():
    data = {{}}
{input_code_str}
    for col in feature_columns:
        data[col] = locals()[col]
    return pd.DataFrame([data])

if st.button("🚀 Predict"):
    df = user_input_features()
    try:
        pred = model.predict(df)[0]
    except:
        from pycaret.classification import predict_model
        pred_df = predict_model(model, data=df)
        pred = pred_df['prediction_label'].iloc[0]
    st.success(f"**Prediction: {{pred}}**")
'''
    return template

def generate_web_app_zip(model_path, feature_columns, feature_types, app_dir="temp_app"):
    """
    Generate ZIP with ready-to-run Streamlit app.
    Args:
        model_path: path to saved model.pkl
        feature_columns: list of column names (from cleaned data)
        feature_types: dict {'col': 'numeric'/'categorical'}
    """
    os.makedirs(app_dir, exist_ok=True)

    # 1. app_model.py
    app_template = generate_app_template(feature_columns, feature_types)
    with open(os.path.join(app_dir, "app_model.py"), "w", encoding="utf-8") as f:
        f.write(app_template)

    # 2. Copy model
    shutil.copy(model_path, os.path.join(app_dir, "model.pkl"))

    # 3. requirements.txt
    reqs = """streamlit
pandas
scikit-learn
joblib
"""
    with open(os.path.join(app_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(reqs)

    # 4. Dockerfile
    dockerfile = """FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app_model.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
    with open(os.path.join(app_dir, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(dockerfile)

    # 5. README
    readme = f"""# My ML Model Web App
Generated: {datetime.now().strftime('%Y-%m-%d')}

## Local Run
pip install -r requirements.txt
streamlit run app_model.py

## Docker Deploy
docker build -t my-model-app .
docker run -p 8501:8501 my-model-app
"""
    with open(os.path.join(app_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    # 6. ZIP
    zip_path = f"my_model_app_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(app_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, app_dir)
                zipf.write(full_path, arcname)

    shutil.rmtree(app_dir)
    return zip_path




# Load custom CSS

# Load custom CSS
def load_css():
    """Load custom CSS styling"""
    css_path = Path(__file__).parent / "static" / "style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False
if 'model_result' not in st.session_state:
    st.session_state.model_result = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None


def show_hero_section():
    """Display hero section"""
    st.markdown("""
    <div class="hero-section fade-in">
        <h1 class="hero-title">🤖 PromptML Studio</h1>
        <p class="hero-subtitle">
            CSV + Prompt = Production ML Model
        </p>
        <p style="font-size: 1.1rem; color: rgba(255,255,255,0.8);">
            Upload your data, describe your goal in natural language, 
            and get production-ready ML models instantly!
        </p>
    </div>
    """, unsafe_allow_html=True)


def show_mode_selector():
    """Display mode selection cards"""
    st.markdown("### 🎯 Choose Your Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 No-Code Mode", width="stretch", type="primary"):
            st.session_state.mode = "no-code"
            st.rerun()
        
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">📱</div>
            <div class="mode-title">No-Code Mode</div>
            <div class="mode-description">
                Perfect for business users and analysts. 
                Get interactive charts, metrics, and PDF reports.
                No coding required!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("💻 Developer Mode", width="stretch", type="secondary"):
            st.session_state.mode = "developer"
            st.rerun()
        
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">💻</div>
            <div class="mode-title">Developer Mode</div>
            <div class="mode-description">
                For developers and ML engineers. 
                Download complete Python package with model files,
                scripts, and tests.
            </div>
        </div>
        """, unsafe_allow_html=True)


def upload_data_section():
    """Data upload section"""
    st.markdown("### 📊 Upload Your Dataset")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Drag and drop your CSV file here",
        type=['csv'],
        help="Upload a CSV file with your dataset"
    )
    
    # Sample data option
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Use House Prices Sample", width="stretch"):
            sample_path = Path(__file__).parent / "static" / "sample_data" / "house_prices.csv"
            if sample_path.exists():
                st.session_state.uploaded_data = pd.read_csv(sample_path)
                st.session_state.sample_prompt = "Predict house prices based on features"
                st.success("✅ House prices sample data loaded!")
                st.rerun()
    
    with col2:
        if st.button("📝 Use Customer Churn Sample", width="stretch"):
            sample_path = Path(__file__).parent / "static" / "sample_data" / "customer_churn.csv"
            if sample_path.exists():
                st.session_state.uploaded_data = pd.read_csv(sample_path)
                st.session_state.sample_prompt = "Classify customer churn risk"
                st.success("✅ Customer churn sample data loaded!")
                st.rerun()
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_data = df
            st.success(f"✅ File uploaded successfully! {len(df)} rows, {len(df.columns)} columns")
            
            # Show preview
            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width="stretch")
                
                # Data info
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Rows", len(df))

                with col2:
                    st.metric("Total Columns", len(df.columns))

                with col3:
                    st.metric("Numeric Columns", len(df.select_dtypes(include=[np.number]).columns))

                with col4:
                    st.metric("Categorical Columns", len(df.select_dtypes(include=['object']).columns))

        
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    
    elif st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        st.success(f"✅ Data loaded! {len(df)} rows, {len(df.columns)} columns")
        
        with st.expander("📋 Data Preview", expanded=False):
            st.dataframe(df.head(10), width="stretch")
    
    return st.session_state.uploaded_data


def prompt_input_section():
    """Prompt input section"""
    st.markdown("### 💬 Describe Your ML Task")
    
    # Get default prompt if sample data was loaded
    default_prompt = st.session_state.get('sample_prompt', '')
    
    prompt = st.text_area(
        "What do you want to predict or classify?",
        value=default_prompt,
        placeholder="Examples:\n- Predict house prices based on features\n- Classify customer churn risk\n- Forecast sales for next quarter\n- Detect fraudulent transactions",
        height=100
    )
    
    return prompt


def train_model_section(df, prompt):
    """Model training section"""
    if st.button("🚀 Build ML Model", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is analyzing your data and building models..."):
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Parse prompt
                status_text.text("🔍 Parsing your prompt...")
                progress_bar.progress(20)
                
                parser = PromptParser()
                task_info = parser.parse_prompt(prompt, df)
                
                st.info(f"✅ Detected Task: **{task_info['task_type'].title()}**")
                st.info(f"✅ Target Column: **{task_info['target_column']}**")
                st.info(f"✅ Confidence: **{task_info['confidence']:.0%}**")
                
                # Step 2: Build model
                status_text.text("🏗️ Training multiple ML models...")
                progress_bar.progress(40)
                
                builder = ModelBuilder()
                result = builder.build_model(
                    df=df,
                    target_column=task_info['target_column'],
                    task_type=task_info['task_type']
                )

                # Add report generator and target column to result
                from backend.ml_engine.report_generator import ReportGenerator
                report_gen = ReportGenerator()
                result['report_generator'] = report_gen
                result['target_column'] = task_info['target_column']

                # Generate charts for display
                charts = report_gen.generate_visualizations(
                    metrics=result['metrics'],
                    feature_importance=result.get('feature_importance', pd.DataFrame()),
                    predictions=result.get('predictions', pd.DataFrame()),
                    task_type=result['task_type']
                )
                result['charts'] = charts

                # Save artifacts

                from backend.ml_engine.model_persistence import save_artifacts

                features = df.drop(columns=[task_info['target_column']]).columns.tolist()

                save_artifacts(
                    model=result['model'],
                    feature_columns=features,
                    task_type=task_info['task_type']
                )

                progress_bar.progress(70)
                
                # Step 3: Generate visualizations
                status_text.text("📊 Generating visualizations...")
                
                report_gen = ReportGenerator()
                charts = report_gen.generate_visualizations(
                    metrics=result['metrics'],
                    feature_importance=result['feature_importance'],
                    predictions=result['predictions'],
                    task_type=task_info['task_type']
                )
                
                progress_bar.progress(90)
                
                # Store results
                st.session_state.model_result = {
                    'model': result['model'],
                    'metrics': result['metrics'],
                    'feature_importance': result['feature_importance'],
                    'predictions': result['predictions'],
                    'charts': charts,
                    'task_type': task_info['task_type'],
                    'target_column': task_info['target_column'],
                    'report_generator': report_gen,
                    'comparison': result['comparison']
                }
                st.session_state.model_trained = True
                
                progress_bar.progress(100)
                status_text.text("✅ Model training complete!")
                
                st.success("🎉 Model trained successfully!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error during model training: {str(e)}")
                st.exception(e)


def show_results_no_code():
    """Display results for no-code mode"""

    if not st.session_state.model_trained or st.session_state.model_result is None:
        return
    
    result = st.session_state.model_result
    metrics = result.get("metrics", {})
    charts = result.get("charts", {})
    task_type = result.get("task_type")

    st.markdown("---")
    st.markdown("## 📊 Model Results")

    if task_type == 'classification':
        st.markdown("### 🎯 Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
        with col2:
            st.metric("Precision", f"{metrics.get('precision', 0):.2%}")
        with col3:
            st.metric("Recall", f"{metrics.get('recall', 0):.2%}")
        with col4:
            st.metric("F1 Score", f"{metrics.get('f1_score', 0):.2%}")

        st.info(f"🤖 Best Model: **{metrics.get('model_name', 'Unknown')}**")

        acc = metrics.get('accuracy', 0)
        if acc >= 0.99:
            st.warning("⚠️ Accuracy is suspiciously high (≥99%). Check if the target column is leaking into features.")

    elif task_type == 'regression':
        st.markdown("### 🎯 Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("R2 Score", f"{metrics.get('r2_score', 0):.4f}")
        with col2:
            st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
        with col3:
            st.metric("MAE", f"{metrics.get('mae', 0):.2f}")
        with col4:
            rmse = metrics.get('rmse', 0)
            st.metric("MSE", f"{rmse**2:.2f}")

        st.info(f"🤖 Best Model: **{metrics.get('model_name', 'Unknown')}**")

        r2 = metrics.get('r2_score', 0)
        if r2 >= 0.99:
            st.warning(f"⚠️ R² is suspiciously perfect ({r2:.4f}). Possible data leakage — check if any feature is derived from the target.")
        elif r2 < 0.5:
            st.warning(f"⚠️ R² Score is low ({r2:.4f}). The model may not be fitting the data well. Consider checking your features or target column.")

    # ── Model comparison table (shown for ALL task types) ──────────
    if result.get('comparison') is not None and not result['comparison'].empty:
        with st.expander("📊 View All Models Comparison", expanded=False):
            comp_df = result['comparison']
            numeric_cols = comp_df.select_dtypes(include='number').columns.tolist()
            try:
                styled = comp_df.style.highlight_max(subset=numeric_cols[:1], color='#1a472a') if numeric_cols else comp_df.style
                st.dataframe(styled, use_container_width=True)
            except Exception:
                st.dataframe(comp_df, use_container_width=True)

    if task_type == 'classification':
        st.markdown("### 📈 Visualizations")
        if 'feature_importance' in charts:
            st.plotly_chart(charts['feature_importance'], use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            if 'confusion_matrix' in charts:
                st.plotly_chart(charts['confusion_matrix'], use_container_width=True)
        with col2:
            if 'metrics_comparison' in charts:
                st.plotly_chart(charts['metrics_comparison'], use_container_width=True)

    elif task_type == 'regression':
        st.markdown("### 📈 Visualizations")
        col1, col2 = st.columns(2)
        with col1:
            if 'actual_vs_predicted' in charts:
                st.plotly_chart(charts['actual_vs_predicted'], use_container_width=True)
        with col2:
            if 'residuals' in charts:
                st.plotly_chart(charts['residuals'], use_container_width=True)

    elif task_type == 'clustering':
        st.markdown("### 🔵 Clustering Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Number of Clusters", metrics.get("n_clusters", 0))
        with col2:
            st.metric("Algorithm", metrics.get("algorithm", "KMeans"))

        st.markdown("### 📋 Clustered Data Preview")
        if 'predictions' in result:
            st.dataframe(result['predictions'].head(), use_container_width=True)

        if "viz_data" in result:
            import plotly.express as px
            fig = px.scatter(
                result["viz_data"],
                x="pca_1",
                y="pca_2",
                color="cluster",
                title="Cluster Visualization (PCA Projection)"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📥 Download Results")
    col1, col2 = st.columns(2)

    with col1:
        if "predictions" in result:
            predictions_csv = result['predictions'].to_csv(index=False)
            st.download_button(
                label="📊 Download Predictions CSV",
                data=predictions_csv,
                file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col2:
        if task_type in ['classification', 'regression' ] and 'report_generator' in result:
            if st.button("📄 Generate PDF Report", use_container_width=True):
                with st.spinner("Generating PDF report..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            pdf_path = tmp_file.name

                        dataset_info = {
                            'n_samples': len(st.session_state.uploaded_data),
                            'n_features': len(st.session_state.uploaded_data.columns),
                            'target_column': result.get('target_column')
                        }

                        result['report_generator'].generate_pdf_report(
                            output_path=pdf_path,
                            metrics=result['metrics'],
                            feature_importance=result.get('feature_importance', pd.DataFrame()),
                            task_type=task_type,
                            dataset_info=dataset_info,
                            predictions=result.get('predictions'),
                            df=st.session_state.uploaded_data
                        )

                        with open(pdf_path, 'rb') as f:
                            pdf_data = f.read()

                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_data,
                            file_name=f"promptml_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

                        os.unlink(pdf_path)

                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")

def show_results_developer():
    """Display results for developer mode"""
    if not st.session_state.model_trained or st.session_state.model_result is None:
        return
    
    result = st.session_state.model_result
    
    st.markdown("---")
    st.markdown("## 💻 Developer Package")
    
    # Show metrics summary
    st.markdown("### 📊 Model Summary")
    metrics = result['metrics']
    st.info(f"🤖 Model: **{metrics.get('model_name', 'Unknown')}**")
    
    if result['task_type'] == 'classification':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
        with col2:
            st.metric("Precision", f"{metrics.get('precision', 0):.2%}")
        with col3:
            st.metric("Recall", f"{metrics.get('recall', 0):.2%}")
        with col4:
            st.metric("F1 Score", f"{metrics.get('f1_score', 0):.2%}")
        acc = metrics.get('accuracy', 0)
        if acc >= 0.99:
            st.warning("⚠️ Accuracy is suspiciously high (≥99%). Check if the target column is leaking into features.")
    elif result['task_type'] == 'regression':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("R² Score", f"{metrics.get('r2_score', 0):.4f}")
        with col2:
            st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
        with col3:
            st.metric("MAE", f"{metrics.get('mae', 0):.2f}")
        with col4:
            rmse = metrics.get('rmse', 0)
            st.metric("MSE", f"{rmse**2:.2f}")
        r2 = metrics.get("r2_score", 0)
        if r2 >= 0.99:
            st.warning(f"⚠️ R² is suspiciously perfect ({r2:.4f}). Possible data leakage — check if any feature is derived from the target.")
        elif r2 < 0.5:
            st.warning(f"⚠️ R² Score is low ({r2:.4f}). Model may not be fitting well. Check features or target column.")
    # Model comparison dropdown
    if result.get("comparison") is not None and not result["comparison"].empty:
        with st.expander("📊 View All Models Comparison", expanded=False):
            comp_df = result["comparison"]
            numeric_cols = comp_df.select_dtypes(include="number").columns.tolist()
            try:
                styled = comp_df.style.highlight_max(subset=numeric_cols[:1], color="#1a472a") if numeric_cols else comp_df.style
                st.dataframe(styled, use_container_width=True)
            except Exception:
                st.dataframe(comp_df, use_container_width=True)

    # Charts (same as no-code)
    charts = result.get("charts", {})
    if charts:
        st.markdown("### 📈 Visualizations")
        if result['task_type'] == 'classification':
            if 'feature_importance' in charts:
                st.plotly_chart(charts['feature_importance'], use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                if 'confusion_matrix' in charts:
                    st.plotly_chart(charts['confusion_matrix'], use_container_width=True)
            with col2:
                if 'metrics_comparison' in charts:
                    st.plotly_chart(charts['metrics_comparison'], use_container_width=True)
        elif result['task_type'] == 'regression':
            col1, col2 = st.columns(2)
            with col1:
                if 'actual_vs_predicted' in charts:
                    st.plotly_chart(charts['actual_vs_predicted'], use_container_width=True)
            with col2:
                if 'residuals' in charts:
                    st.plotly_chart(charts['residuals'], use_container_width=True)

    # Downloads section
    st.markdown("### 📥 Download Results")
    col1, col2, col3 = st.columns(3)

    # Col 1 — Predictions CSV
    with col1:
        if "predictions" in result:
            predictions_csv = result['predictions'].to_csv(index=False)
            st.download_button(
                label="📊 Download Predictions CSV",
                data=predictions_csv,
                file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Col 2 — PDF Report (same as no-code)
    with col2:
        if result['task_type'] in ['classification', 'regression'] and 'report_generator' in result:
            if st.button("📄 Generate PDF Report", use_container_width=True, key="dev_pdf_btn"):
                with st.spinner("Generating PDF report..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            pdf_path = tmp_file.name

                        dataset_info = {
                            'n_samples': len(st.session_state.uploaded_data),
                            'n_features': len(st.session_state.uploaded_data.columns),
                            'target_column': result.get('target_column')
                        }

                        result['report_generator'].generate_pdf_report(
                            output_path=pdf_path,
                            metrics=result['metrics'],
                            feature_importance=result.get('feature_importance', pd.DataFrame()),
                            task_type=result['task_type'],
                            dataset_info=dataset_info,
                            predictions=result.get('predictions'),
                            df=st.session_state.uploaded_data
                        )

                        with open(pdf_path, 'rb') as f:
                            pdf_data = f.read()

                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_data,
                            file_name=f"promptml_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

                        os.unlink(pdf_path)

                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")

    # Col 3 — Python Package ZIP
    with col3:
        if st.button("🔨 Generate Python Package", use_container_width=True, key="dev_pkg_btn"):
            with st.spinner("Creating production package..."):
                try:
                    feature_columns = st.session_state.uploaded_data.drop(columns=[result['target_column']]).columns.tolist()
                    feature_types = infer_types(st.session_state.uploaded_data.drop(columns=[result['target_column']]))
                    sample_data = st.session_state.uploaded_data.drop(columns=[result['target_column']])
                    app_template = generate_app_template(feature_columns, feature_types, sample_data)

                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        import joblib
                        model_buffer = io.BytesIO()
                        joblib.dump(result['model'], model_buffer)
                        zip_file.writestr('model.pkl', model_buffer.getvalue())

                        metrics_buffer = io.BytesIO()
                        joblib.dump(result['metrics'], metrics_buffer)
                        zip_file.writestr('metrics.pkl', metrics_buffer.getvalue())

                        if not result['feature_importance'].empty:
                            zip_file.writestr('feature_importance.csv', result['feature_importance'].to_csv(index=False))

                        task_type = result['task_type']
                        predict_script = f'''"""Prediction Script - PromptML Studio\nTask: {task_type}"""\nimport pandas as pd\nimport joblib\nimport sys\n\nmodel = joblib.load("model.pkl")\n\ndef predict(data_path):\n    df = pd.read_csv(data_path)\n    try:\n        from pycaret.{task_type} import predict_model\n        return predict_model(model, data=df)\n    except:\n        preds = model.predict(df)\n        df["prediction"] = preds\n        return df\n\nif __name__ == "__main__":\n    result = predict(sys.argv[1])\n    result.to_csv("predictions_output.csv", index=False)\n    print(f"Done! {{len(result)}} predictions saved.")\n'''
                        zip_file.writestr('predict.py', predict_script)
                        zip_file.writestr('requirements.txt', "pandas\nnumpy\nscikit-learn\npycaret==3.3.2\njoblib\n")

                        readme = f"# PromptML Model Package\n**Task:** {task_type.title()}\n**Model:** {metrics.get('model_name','Unknown')}\n\n## Run\n```bash\npip install -r requirements.txt\npython predict.py your_data.csv\n```\n"
                        zip_file.writestr('README.md', readme)

                    zip_buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download Package (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name=f"promptml_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    st.success("✅ Package ready!")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.exception(e)
def run_generated_app():
    """Run the generated application preview."""
    if st.session_state.get("preview_html"):
        import streamlit.components.v1 as components
        components.html(st.session_state["preview_html"], height=700, scrolling=True)
    else:
        st.warning("⚠️ Preview not generated. Please build the website first in the 'Deploy as Website' section.")

def deploy_to_render():
    """Step-by-step Render deployment guide."""

    st.markdown("### 🚀 Deploy Your ML App on Render — Step by Step")
    st.caption("Render gives you a **free live URL** so anyone can use your model from anywhere.")

    st.markdown("---")

    # Step 1
    with st.expander("✅ Step 1 — Download the Website ZIP", expanded=True):
        st.markdown("""
        - Go back to the **Studio** and click **⬇️ Download Website ZIP**
        - This ZIP contains your `app.py`, `model.pkl`, and `requirements.txt`
        - Save it somewhere easy to find on your computer
        """)

    # Step 2
    with st.expander("✅ Step 2 — Create a GitHub Repository", expanded=True):
        st.markdown("""
        1. Go to [github.com](https://github.com) and sign in (or create a free account)
        2. Click **New Repository** → give it a name like `my-ml-app`
        3. Set it to **Public** → click **Create Repository**
        4. Extract the ZIP and **upload all 3 files** (`app.py`, `model.pkl`, `requirements.txt`) to the repo
        """)
        st.info("💡 Tip: Use **Add file → Upload files** on GitHub — no Git knowledge needed!")

    # Step 3
    with st.expander("✅ Step 3 — Deploy on Render (Free)", expanded=True):
        st.markdown("""
        1. Go to [render.com](https://render.com) and sign in with GitHub
        2. Click **New → Web Service**
        3. Select your GitHub repo (`my-ml-app`)
        4. Fill in these settings:
        """)
        st.code("""
Name        : my-ml-app          (anything you like)
Environment : Python
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
        """, language="bash")
        st.markdown("""
        5. Choose **Free** plan → Click **Create Web Service**
        6. Wait ~3-5 minutes for the first build to finish
        7. Render gives you a link like: `https://my-ml-app.onrender.com` 🎉
        """)
        st.success("✅ Your app is now live! Share the link with anyone.")

    # Step 4 — Troubleshooting
    with st.expander("⚠️ Common Issues & Fixes"):
        st.markdown("""
        | Problem | Fix |
        |---|---|
        | Build fails with PyCaret error | Make sure `requirements.txt` has `pycaret==3.1.0` |
        | App crashes on start | Check Start Command has `--server.address 0.0.0.0` |
        | Model not loading | Ensure `model.pkl` is uploaded to the repo |
        | App sleeps after 15 mins | Free tier spins down — first visit after sleep takes ~30s |
        """)
        st.markdown("Still stuck? Check [Render Docs](https://render.com/docs) or ask the PromptML AI Assistant.")


def main():

    # ---------- SESSION STATE (TOP) ----------
    if "mode" not in st.session_state:
        st.session_state.mode = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Preview Mode Session
    if "preview_mode" not in st.session_state:
        st.session_state.preview_mode = False
    if "local_app_ready" not in st.session_state:
        st.session_state.local_app_ready = False
    if "local_app_error" not in st.session_state:
        st.session_state.local_app_error = None

    # ==============================
    # FULL SCREEN PREVIEW MODE
    # ==============================
    if st.session_state.preview_mode:

        # Hide header + footer
        st.markdown("""
            <style>
                header {visibility: hidden;}
                footer {visibility: hidden;}
                .block-container {padding-top: 1rem;}
            </style>
        """, unsafe_allow_html=True)

        # 🔹 RUN GENERATED APP
        run_generated_app()   # <-- ye tumhara existing function hona chahiye

        st.divider()

        col1, col2 = st.columns(2)

        # 🔙 Back Button
        with col1:
            if st.button("⬅ Back to Studio", use_container_width=True):
                st.session_state.preview_mode = False
                st.rerun()

        # 🚀 Deploy to Render Button
        with col2:
            if st.button("🚀 Deploy to Render", use_container_width=True, type="primary"):
                deploy_to_render()

        st.stop()

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.markdown("## 🤖 PromptML Assistant")
        st.caption("ML • Data Science • Computer Science • Your Results")

        # Build context from current session
        context_block = ""
        if st.session_state.get("model_trained") and st.session_state.get("model_result"):
            r = st.session_state.model_result
            m = r.get("metrics", {})
            context_block = f"""
CURRENT SESSION CONTEXT:
- Task Type    : {r.get('task_type', 'N/A')}
- Target Column: {r.get('target_column', 'N/A')}
- Best Model   : {m.get('model_name', 'N/A')}
"""
            if r.get("task_type") == "classification":
                context_block += f"- Accuracy: {m.get('accuracy','N/A')} | F1: {m.get('f1_score','N/A')}\n"
            elif r.get("task_type") == "regression":
                context_block += f"- R2: {m.get('r2_score','N/A')} | RMSE: {m.get('rmse','N/A')}\n"
            if st.session_state.get("uploaded_data") is not None:
                df_info = st.session_state.uploaded_data
                context_block += f"- Dataset: {df_info.shape[0]} rows x {df_info.shape[1]} cols\n"

        system_prompt = f"""You are PromptML Studio's expert AI assistant.

Your expertise covers:
1. PROMPTML STUDIO - every feature, workflow, AutoML, PyCaret, model selection, deployment
2. MACHINE LEARNING - any algorithm, concept (overfitting, cross-validation, ensemble), metrics (Accuracy, F1, RMSE, R2, AUC)
3. DATA SCIENCE - EDA, feature engineering, pandas, numpy, matplotlib, seaborn, plotly
4. COMPUTER SCIENCE - Python, algorithms, Docker, Git, APIs, cloud deployment
5. USER RESULTS - explain their specific metrics and give improvement tips

STYLE:
- When explaining PromptML Studio features, use simple plain English — no code, no jargon
- Imagine you are explaining to someone who has never used ML before
- Use real life analogies and examples (e.g. "Accuracy is like a test score out of 100")
- For technical ML/CS questions from developers, be technical and precise
- Use bullet points for steps, keep sentences short
- Always be encouraging and friendly
- End answers with 1 simple actionable tip

{context_block}"""

         # Prompt Refiner
        st.markdown("**✨ Prompt Refiner**")
        user_raw_prompt = st.text_input(
            "Paste your prompt to refine:",
            placeholder="e.g. predict sales, classify churn...",
            key="prompt_refiner_input"
        )
        if st.button("✨ Refine My Prompt", use_container_width=True, key="refine_btn"):
            if user_raw_prompt.strip():
                refine_question = (
                    f"Refine and improve this ML prompt for use in PromptML Studio. "
                    f"It should clearly mention: what to predict or classify, "
                    f"the target column if obvious, and the task type "
                    f"(regression/classification/clustering). "
                    f"Give 2-3 improved versions, keep them short and natural. "
                    f"My original prompt: '{user_raw_prompt}'"
                )
                st.session_state.chat_history.append(
                    {"role": "user", "content": refine_question}
                )
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
                    groq_response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=1024,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *[{"role": m["role"], "content": m["content"]}
                              for m in st.session_state.chat_history
                              if m["role"] in ("user", "assistant")]
                        ]
                    )
                    bot_reply = groq_response.choices[0].message.content
                except Exception as e:
                    bot_reply = f"⚠️ Groq error: {e}"
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": bot_reply}
                )
                st.rerun()

        # FAQs Dropdown
        faq_options = {
            "— Select a question —": "",
            "📌 How do I use PromptML Studio?": "Explain how to use PromptML Studio step by step in simple non-technical terms for a beginner",
            "📌 Why is my dataset not working?": "Why might my CSV dataset not work in PromptML Studio and how do I fix it?",
            "📌 Why are my results so low?": "My model results are very low, what could be wrong and how do I improve them?",
            "📌 What is Accuracy?": "Explain Accuracy in machine learning in very simple terms with a real life example",
            "📌 What is R² score?": "Explain R² score in very simple terms with a real life example",
            "📌 What is RMSE?": "Explain RMSE in very simple terms with a real life example",
            "📌 What does the best model mean?": "What does best model mean in PromptML Studio and why was it selected?",
            "📌 What is feature importance?": "Explain feature importance in simple terms, why does it matter?",
            "📌 No-Code vs Developer Mode?": "What is the difference between No-Code Mode and Developer Mode in PromptML Studio in simple terms?",
            "📌 How to improve my model?": "Give me simple practical tips to improve my machine learning model results",
            "📌 What is overfitting?": "Explain overfitting in very simple non-technical terms with a real life example",
            "📌 How to deploy my model?": "How do I deploy my trained model from PromptML Studio as a live website in simple steps?",
        }

        selected_faq = st.selectbox(
            "💡 FAQs & Quick Questions",
            options=list(faq_options.keys()),
            key="faq_select"
        )

        if selected_faq != "— Select a question —":
            if st.button("Ask this ➤", use_container_width=True, key="faq_btn"):
                question = faq_options[selected_faq]
                st.session_state.chat_history.append(
                    {"role": "user", "content": question}
                )
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
                    groq_response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=1024,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *[{"role": m["role"], "content": m["content"]}
                              for m in st.session_state.chat_history
                              if m["role"] in ("user", "assistant")]
                        ]
                    )
                    bot_reply = groq_response.choices[0].message.content
                except Exception as e:
                    bot_reply = f"⚠️ Groq error: {e}"
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": bot_reply}
                )
                st.rerun()

        prefill = st.session_state.pop("prefill_question", "")
        user_input = st.text_input(
            "Ask me anything...",
            value=prefill,
            placeholder="e.g. What is Random Forest? Why is R² negative?",
            key="chat_input"
        )

        send_col, clear_col = st.columns([2, 1])
        send_clicked  = send_col.button("Send ➤", use_container_width=True, type="primary")
        clear_clicked = clear_col.button("🗑️ Clear", use_container_width=True)

        if clear_clicked:
            st.session_state.chat_history = []
            st.rerun()

        if send_clicked and user_input.strip():
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input.strip()}
            )

            bot_reply = None

            # --- Groq API ---
            try:
                from groq import Groq
                groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
                groq_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.chat_history
                          if m["role"] in ("user", "assistant")]
                    ]
                )
                bot_reply = groq_response.choices[0].message.content
            except Exception as e:
                bot_reply = (
                    "⚠️ **Groq API error.**\n\n"
                    "Make sure `GROQ_API_KEY` is set.\n"
                    "Get free key at: https://console.groq.com\n\n"
                    f"_Error: {e}_"
                )

            st.session_state.chat_history.append(
                {"role": "assistant", "content": bot_reply}
            )
            st.rerun()

        # Chat display
        st.markdown("---")
        for msg in reversed(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(
                    f"<div style='background:#1e1e2e;padding:8px 12px;border-radius:8px;"
                    f"margin-bottom:6px;border-left:3px solid #6c63ff'>"
                    f"🧑 <b>You:</b> {msg['content']}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='background:#0f2a1a;padding:8px 12px;border-radius:8px;"
                    f"margin-bottom:10px;border-left:3px solid #2ecc71'>"
                    f"🤖 <b>Assistant:</b><br>{msg['content']}</div>",
                    unsafe_allow_html=True
                )

        st.markdown("---")
       
# -------------------- REST OF YOUR APP --------------------
# Existing UI, No-Code mode, Developer mode, etc.

        
        # Mode indicator
        if st.session_state.mode:
            mode_emoji = "📱" if st.session_state.mode == "no-code" else "💻"
            st.info(f"{mode_emoji} **{st.session_state.mode.title()} Mode**")
            
            if st.button("🔄 Change Mode"):
                st.session_state.mode = None
                st.session_state.model_trained = False
                st.session_state.model_result = None
                st.rerun()
        
        st.markdown("---")
        
        # Info
        st.markdown("### 📚 About")
        st.markdown("""
        **PromptML Studio** is an AI-powered AutoML platform that 
        democratizes machine learning.
        
        Simply upload your data, describe your goal, and get 
        production-ready ML models!
        """)
        
        st.markdown("---")
        st.markdown("### 🎓 AIML Diploma Project")
        st.markdown("Made with ❤️ for democratizing AI/ML")
    
    # Main content
    if st.session_state.mode is None:
        show_hero_section()
        show_mode_selector()
    
    else:
        # Show header
        st.title(f"{'📱 No-Code' if st.session_state.mode == 'no-code' else '💻 Developer'} Mode")
        
        # Upload data
        df = upload_data_section()
        
        if df is not None:
            # Prompt input
            prompt = prompt_input_section()
            
            if prompt:
                # Train model
                train_model_section(df, prompt)
                
                # Show results
                if st.session_state.mode == "no-code":
                    show_results_no_code()
                else:
                    show_results_developer()

                                
                # ===============================
                # WEBSITE GENERATION SECTION
                # ===============================

                from backend.ml_engine.website_generator import generate_website, generate_preview_html

                if st.session_state.get("model_trained"):
                    st.markdown("---")
                    st.subheader("🌍 Deploy as Website")

                    if st.button("🚀 Build Website", type="primary", use_container_width=True):
                        with st.spinner("Generating website..."):
                            zip_path = generate_website()
                            st.session_state["website_zip_path"] = zip_path
                            import joblib as _jl
                            _features = _jl.load("artifacts/features.pkl")
                            _task_type = _jl.load("artifacts/task_type.pkl")
                            st.session_state["preview_html"] = generate_preview_html(_features, _task_type)

                    if st.session_state.get("website_zip_path"):
                        saved_zip_path = st.session_state["website_zip_path"]
                        st.success("✅ Website generated successfully!")

                        btn_col1, btn_col2 = st.columns(2)

                        with btn_col1:
                            with open(saved_zip_path, "rb") as f:
                                st.download_button(
                                    "⬇️ Download Website ZIP",
                                    f,
                                    file_name="promptml_website.zip",
                                    mime="application/zip",
                                    use_container_width=True,
                                )

                        with btn_col2:
                            if st.button("👁️ Preview / Deploy", use_container_width=True):
                                st.session_state.preview_mode = True
                                st.rerun()

                
if __name__ == "__main__":
    main()