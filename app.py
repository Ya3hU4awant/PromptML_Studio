"""
PromptML Studio - Main Streamlit Application
AI-Powered AutoML Platform with Dual-Mode Interface
"""
import requests
import streamlit as st
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

sys.path.append(str(Path(__file__).parent))

from backend.ml_engine.prompt_parser import PromptParser
from backend.ml_engine.model_builder import ModelBuilder
from backend.ml_engine.report_generator import ReportGenerator
from backend.ml_engine.website_generator import generate_website
from backend.predictor import Predictor
from how_it_works import show_how_it_works_page
from features import show_features_page
from contact import show_contact_page
from privacy import show_privacy_page

# ── Cached singletons — instantiated once, reused across reruns ──
@st.cache_resource
def get_prompt_parser():
    return PromptParser()

@st.cache_resource
def get_model_builder():
    return ModelBuilder()

@st.cache_resource
def get_report_generator():
    return ReportGenerator()

# ─────────────────────────────────────────────────────────────
# NAVIGATION HELPER  — use this everywhere instead of
# touching st.session_state.current_page directly
# ─────────────────────────────────────────────────────────────
def navigate_to(page: str):
    """
    Central navigation function.
    page = 'home' | 'about' | 'how_it_works' | 'features' | ...
    Add new pages here as the project grows.
    """
    VALID_PAGES = {"home", "about", "how_it_works", "features"}
    if page not in VALID_PAGES:
        page = "home"
    st.session_state.current_page = page
    if page == "home":
        # Reset mode when going home so hero screen shows
        st.session_state.mode = None
    st.rerun()


# ─────────────────────────────────────────────────────────────
# PAGE IMPORTS
# ─────────────────────────────────────────────────────────────
from about import show_about_page


# ─────────────────────────────────────────────────────────────
# WEB APP GENERATOR HELPERS
# ─────────────────────────────────────────────────────────────
@st.cache_data
def infer_types(df):
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
    input_code = []
    cat_options = {}
    if sample_data is not None:
        for col in feature_columns:
            if feature_types.get(col) == 'categorical':
                unique_vals = sample_data[col].dropna().unique()[:10]
                cat_options[col] = [str(v) for v in unique_vals]
    for col in feature_columns:
        ftype = feature_types.get(col, 'numeric')
        if ftype == 'numeric':
            input_code.append(f"    {col} = st.number_input('{col}', value=0.0)")
        elif ftype == 'categorical':
            options = cat_options.get(col, ['Option1', 'Option2'])
            input_code.append(f"    {col} = st.selectbox('{col}', {repr(options)})")
        else:
            input_code.append(f"    {col} = st.text_input('{col}')")
    input_code_str = "\n".join(input_code)
    template = f'''import streamlit as st
import pandas as pd
import joblib

@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

model = load_model()
feature_columns = {repr(feature_columns)}

st.title("ML Model Predictor")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    try:
        predictions = model.predict(df[feature_columns])
    except:
        from pycaret.classification import predict_model
        preds = predict_model(model, data=df[feature_columns])
        predictions = preds['prediction_label']
    st.write("Predictions:", predictions)
    st.stop()

st.header("Single Prediction")
def user_input_features():
    data = {{}}
{input_code_str}
    for col in feature_columns:
        data[col] = locals()[col]
    return pd.DataFrame([data])

if st.button("Predict"):
    df = user_input_features()
    try:
        pred = model.predict(df)[0]
    except:
        from pycaret.classification import predict_model
        pred_df = predict_model(model, data=df)
        pred = pred_df['prediction_label'].iloc[0]
    st.success(f"Prediction: {{pred}}")
'''
    return template


def generate_web_app_zip(model_path, feature_columns, feature_types, app_dir="temp_app"):
    os.makedirs(app_dir, exist_ok=True)
    app_template = generate_app_template(feature_columns, feature_types)
    with open(os.path.join(app_dir, "app_model.py"), "w", encoding="utf-8") as f:
        f.write(app_template)
    shutil.copy(model_path, os.path.join(app_dir, "model.pkl"))
    reqs = "streamlit\npandas\nscikit-learn\njoblib\n"
    with open(os.path.join(app_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(reqs)
    zip_path = f"my_model_app_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(app_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, app_dir)
                zipf.write(full_path, arcname)
    shutil.rmtree(app_dir)
    return zip_path


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG & CSS
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PromptML Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "**PromptML Studio** — Democratizing AI/ML for everyone.\n\nBuilt by Ya3hU4awant"
    }
)

def load_css():
    css_path = Path(__file__).parent / "static" / "style.css"
    if css_path.exists():
        with open(css_path, encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* ── Hide ALL Streamlit branding — desktop + mobile ── */

    /* Main menu hamburger */
    #MainMenu {visibility: hidden !important; display: none !important;}

    /* Footer "Made with Streamlit" */
    footer {visibility: hidden !important; display: none !important;}
    footer *  {visibility: hidden !important; display: none !important;}

    /* Top decoration bar */
    [data-testid="stDecoration"]       {display: none !important;}

    /* Status widget (running indicator) */
    [data-testid="stStatusWidget"]     {display: none !important;}

    /* Viewer badge (bottom-right Streamlit logo on mobile) */
    .viewerBadge_container__r5tak      {display: none !important;}
    .viewerBadge_link__qRIco           {display: none !important;}
    .viewerBadge_text__1022            {display: none !important;}
    [class*="viewerBadge"]             {display: none !important;}

    /* Manage app / Deploy buttons */
    [data-testid="manage-app-button"]  {display: none !important;}
    [data-testid="stToolbarActions"]   {display: none !important;}

    /* GitHub profile icon bottom-right (mobile + desktop) */
    ._profileContainer_51w34_53        {display: none !important;}
    ._profilePreview_51w34_63          {display: none !important;}
    [class*="profileContainer"]        {display: none !important;}
    [class*="profilePreview"]          {display: none !important;}
    [data-testid="baseButton-header"][aria-label*="profile"] {display: none !important;}
    [data-testid="baseButton-header"][aria-label*="GitHub"]  {display: none !important;}
    [data-testid="baseButton-header"][title*="GitHub"]       {display: none !important;}

    /* Streamlit cloud bottom-right watermark */
    [data-testid="stAppViewBlockContainer"] ~ div > a        {display: none !important;}
    a[href*="streamlit.io"]                                  {display: none !important;}
    a[href*="share.streamlit"]                               {display: none !important;}

    /* Any element with Streamlit logo SVG */
    img[src*="streamlit"]                                    {display: none !important;}

    /* Mobile: bottom bar that shows on phones */
    [data-testid="stBottomBlockContainer"] [data-testid="stToolbar"] {display: none !important;}

    /* "Created by" text + avatar bottom right */
    [data-testid="stBottom"]                                         {display: none !important;}
    [data-testid="stBottomBlockContainer"]                           {display: none !important;}
    ._container_51w34_1                                              {display: none !important;}
    ._container_gzau3_1                                              {display: none !important;}
    [class*="_container_"][class*="_bottom"]                         {display: none !important;}
    [class*="createdBy"]                                             {display: none !important;}
    [class*="created_by"]                                            {display: none !important;}
    /* Hide the entire fixed bottom-right corner block */
    .stApp > div:last-child > div:last-child > div[style*="position: fixed"] {display: none !important;}
    div[style*="position: fixed"][style*="bottom"]                   {display: none !important;}

    /* GitHub avatar circle + red Streamlit share/crown button (mobile bottom-right) */
    [data-testid="stActionButtonIcon"]                               {display: none !important;}
    button[kind="shareButton"]                                       {display: none !important;}
    button[data-testid="shareButton"]                                {display: none !important;}
    [class*="shareButton"]                                           {display: none !important;}
    [class*="ActionButton"]                                          {display: none !important;}

    /* The entire fixed bottom-right floating bar on mobile */
    section[data-testid="stSidebar"] ~ div > div[class*="fixed"]    {display: none !important;}
    .stApp [class*="floatingToolbar"]                                {display: none !important;}
    [class*="floatingToolbar"]                                       {display: none !important;}
    [class*="toolbar"][style*="fixed"]                               {display: none !important;}

    /* Nuclear option — hide any fixed-position bottom-right element */
    div[style*="position: fixed"][style*="right"]                    {display: none !important;}
    div[style*="position:fixed"][style*="right"]                     {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

load_css()

# ─────────────────────────────────────────────────────────────
# GLOBAL SESSION STATE — initialise ONCE at module level
# so it is always available before any function runs
# ─────────────────────────────────────────────────────────────
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False
if 'model_result' not in st.session_state:
    st.session_state.model_result = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


# ─────────────────────────────────────────────────────────────
# UI SECTIONS
# ─────────────────────────────────────────────────────────────
def show_hero_section():
    st.markdown("""
    <div class="hero-section fade-in">
        <h1 class="hero-title">🤖 PromptML Studio</h1>
        <p class="hero-subtitle">CSV + Prompt = Production ML Model</p>
        <p style="font-size: 1.1rem; color: rgba(255,255,255,0.8);">
            Upload your data, describe your goal in natural language,
            and get production-ready ML models instantly!
        </p>
    </div>
    """, unsafe_allow_html=True)


def show_mode_selector():
    st.markdown("### 🎯 Choose Your Mode")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 No-Code Mode", width='stretch', type="primary"):
            st.session_state.mode = "no-code"
            st.rerun()
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">📱</div>
            <div class="mode-title">No-Code Mode</div>
            <div class="mode-description">
                Perfect for business users and analysts.
                Get interactive charts, metrics, and PDF reports. No coding required!
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("💻 Developer Mode", width='stretch', type="secondary"):
            st.session_state.mode = "developer"
            st.rerun()
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">💻</div>
            <div class="mode-title">Developer Mode</div>
            <div class="mode-description">
                For developers and ML engineers.
                Download complete Python package with model files, scripts, and tests.
            </div>
        </div>
        """, unsafe_allow_html=True)


def upload_data_section():
    st.markdown("### 📊 Upload Your Dataset")
    uploaded_file = st.file_uploader("Drag and drop your CSV file here", type=['csv'])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Use House Prices Sample", width='stretch'):
            sample_path = Path(__file__).parent / "static" / "sample_data" / "house_prices.csv"
            if sample_path.exists():
                st.session_state.uploaded_data = pd.read_csv(sample_path)
                st.session_state.sample_prompt = "Predict house prices based on features"
                st.success("✅ House prices sample data loaded!")
                st.rerun()
    with col2:
        if st.button("📝 Use Customer Churn Sample", width='stretch'):
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
            st.success(f"✅ File uploaded! {len(df)} rows, {len(df.columns)} columns")
            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(df.head(10), width='stretch')
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Total Rows", len(df))
                with col2: st.metric("Total Columns", len(df.columns))
                with col3: st.metric("Numeric Columns", len(df.select_dtypes(include=[np.number]).columns))
                with col4: st.metric("Categorical Columns", len(df.select_dtypes(include=['object']).columns))
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    elif st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        st.success(f"✅ Data loaded! {len(df)} rows, {len(df.columns)} columns")
        with st.expander("📋 Data Preview", expanded=False):
            st.dataframe(df.head(10), width='stretch')
    return st.session_state.uploaded_data


def prompt_input_section():
    st.markdown("### 💬 Describe Your ML Task")
    default_prompt = st.session_state.get('sample_prompt', '')
    prompt = st.text_area(
        "What do you want to predict or classify?",
        value=default_prompt,
        placeholder="Examples:\n- Predict house prices\n- Classify customer churn\n- Detect fraud",
        height=100
    )
    return prompt


def train_model_section(df, prompt):
    if st.button("🚀 Build ML Model", type="primary", width='stretch'):
        with st.spinner("🤖 AI is analyzing your data and building models..."):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("🔍 Parsing your prompt...")
                progress_bar.progress(20)
                parser = get_prompt_parser()
                task_info = parser.parse_prompt(prompt, df)
                st.info(f"✅ Detected Task: **{task_info['task_type'].title()}**")
                st.info(f"✅ Target Column: **{task_info['target_column']}**")
                st.info(f"✅ Confidence: **{task_info['confidence']:.0%}**")
                status_text.text("🏗️ Training multiple ML models...")
                progress_bar.progress(40)
                builder = get_model_builder()
                result = builder.build_model(df=df, target_column=task_info['target_column'], task_type=task_info['task_type'])
                report_gen = get_report_generator()
                result['report_generator'] = report_gen
                result['target_column'] = task_info['target_column']
                charts = report_gen.generate_visualizations(
                    metrics=result['metrics'],
                    feature_importance=result.get('feature_importance', pd.DataFrame()),
                    predictions=result.get('predictions', pd.DataFrame()),
                    task_type=result['task_type']
                )
                result['charts'] = charts
                from backend.ml_engine.model_persistence import save_artifacts
                features = df.drop(columns=[task_info['target_column']]).columns.tolist()
                save_artifacts(model=result['model'], feature_columns=features, task_type=task_info['task_type'])
                progress_bar.progress(90)
                status_text.text("✅ Model training complete!")
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
                st.success("🎉 Model trained successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error during model training: {str(e)}")
                st.exception(e)


def show_results_no_code():
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
        with col1: st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
        with col2: st.metric("Precision", f"{metrics.get('precision', 0):.2%}")
        with col3: st.metric("Recall", f"{metrics.get('recall', 0):.2%}")
        with col4: st.metric("F1 Score", f"{metrics.get('f1_score', 0):.2%}")
        st.info(f"🤖 Best Model: **{metrics.get('model_name', 'Unknown')}**")
        if metrics.get("overfitting_warning"):
            st.warning(metrics["overfitting_warning"])
        st.markdown("### 📈 Visualizations")
        if 'feature_importance' in charts:
            st.plotly_chart(charts['feature_importance'], width='stretch')
        col1, col2 = st.columns(2)
        with col1:
            if 'confusion_matrix' in charts:
                st.plotly_chart(charts['confusion_matrix'], width='stretch')
        with col2:
            if 'metrics_comparison' in charts:
                st.plotly_chart(charts['metrics_comparison'], width='stretch')
    elif task_type == 'regression':
        st.markdown("### 🎯 Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("R2 Score", f"{metrics.get('r2_score', 0):.4f}")
        with col2: st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
        with col3: st.metric("MAE", f"{metrics.get('mae', 0):.2f}")
        with col4:
            rmse = metrics.get('rmse', 0)
            st.metric("MSE", f"{rmse**2:.2f}")
        st.info(f"🤖 Best Model: **{metrics.get('model_name', 'Unknown')}**")
        if metrics.get("overfitting_warning"):
            st.warning(metrics["overfitting_warning"])
        if result.get('comparison') is not None and not result['comparison'].empty:
            with st.expander("📊 View All Models Comparison", expanded=False):
                st.dataframe(result['comparison'], width='stretch')
        st.markdown("### 📈 Visualizations")
        col1, col2 = st.columns(2)
        with col1:
            if 'actual_vs_predicted' in charts:
                st.plotly_chart(charts['actual_vs_predicted'], width='stretch')
        with col2:
            if 'residuals' in charts:
                st.plotly_chart(charts['residuals'], width='stretch')
    elif task_type == 'clustering':
        st.markdown("### 🔵 Clustering Results")
        col1, col2 = st.columns(2)
        with col1: st.metric("Number of Clusters", metrics.get("n_clusters", 0))
        with col2: st.metric("Algorithm", metrics.get("algorithm", "KMeans"))
        if 'predictions' in result:
            st.dataframe(result['predictions'].head(), width='stretch')
        if "viz_data" in result:
            import plotly.express as px
            fig = px.scatter(result["viz_data"], x="pca_1", y="pca_2", color="cluster", title="Cluster Visualization (PCA)")
            st.plotly_chart(fig, width='stretch')
    st.markdown("### 📥 Download Results")
    col1, col2 = st.columns(2)
    with col1:
        if "predictions" in result:
            predictions_csv = result['predictions'].to_csv(index=False)
            st.download_button(
                label="📊 Download Predictions CSV", data=predictions_csv,
                file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv", width='stretch'
            )
    with col2:
        if task_type in ['classification', 'regression'] and 'report_generator' in result:
            if st.button("📄 Generate PDF Report", width='stretch', key="nocode_pdf_btn"):
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
                            output_path=pdf_path, metrics=result['metrics'],
                            feature_importance=result.get('feature_importance', pd.DataFrame()),
                            task_type=task_type, dataset_info=dataset_info,
                            predictions=result.get('predictions'), df=st.session_state.uploaded_data
                        )
                        with open(pdf_path, 'rb') as f:
                            pdf_data = f.read()
                        st.download_button(
                            label="⬇️ Download PDF Report", data=pdf_data,
                            file_name=f"promptml_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf", width='stretch'
                        )
                        os.unlink(pdf_path)
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")


def show_results_developer():
    if not st.session_state.model_trained or st.session_state.model_result is None:
        return
    result = st.session_state.model_result
    st.markdown("---")
    st.markdown("## 💻 Developer Package")
    st.markdown("### 📊 Model Summary")
    metrics = result['metrics']
    st.info(f"🤖 Model: **{metrics.get('model_name', 'Unknown')}**")
    if metrics.get("overfitting_warning"):
        st.warning(metrics["overfitting_warning"])
    if result['task_type'] == 'classification':
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
        with col2: st.metric("Precision", f"{metrics.get('precision', 0):.2%}")
        with col3: st.metric("Recall", f"{metrics.get('recall', 0):.2%}")
        with col4: st.metric("F1 Score", f"{metrics.get('f1_score', 0):.2%}")
    elif result['task_type'] == 'regression':
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("R² Score", f"{metrics.get('r2_score', 0):.4f}")
        with col2: st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
        with col3: st.metric("MAE", f"{metrics.get('mae', 0):.2f}")
        with col4:
            rmse = metrics.get('rmse', 0)
            st.metric("MSE", f"{rmse**2:.2f}")
    if result.get('comparison') is not None and not result['comparison'].empty:
        with st.expander("📊 View All Models Comparison", expanded=False):
            st.dataframe(result['comparison'], width='stretch')
    charts = result.get("charts", {})
    if charts:
        st.markdown("### 📈 Visualizations")
        if result['task_type'] == 'classification':
            if 'feature_importance' in charts:
                st.plotly_chart(charts['feature_importance'], width='stretch')
            col1, col2 = st.columns(2)
            with col1:
                if 'confusion_matrix' in charts:
                    st.plotly_chart(charts['confusion_matrix'], width='stretch')
            with col2:
                if 'metrics_comparison' in charts:
                    st.plotly_chart(charts['metrics_comparison'], width='stretch')
        elif result['task_type'] == 'regression':
            col1, col2 = st.columns(2)
            with col1:
                if 'actual_vs_predicted' in charts:
                    st.plotly_chart(charts['actual_vs_predicted'], width='stretch')
            with col2:
                if 'residuals' in charts:
                    st.plotly_chart(charts['residuals'], width='stretch')
    st.markdown("### 📥 Download Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        if "predictions" in result:
            st.download_button(
                label="📊 Download Predictions CSV",
                data=result['predictions'].to_csv(index=False),
                file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv", width='stretch'
            )
    with col2:
        if result['task_type'] in ['classification', 'regression'] and 'report_generator' in result:
            if st.button("📄 Generate PDF Report", width='stretch', key="dev_pdf_btn"):
                with st.spinner("Generating PDF..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            pdf_path = tmp_file.name
                        dataset_info = {
                            'n_samples': len(st.session_state.uploaded_data),
                            'n_features': len(st.session_state.uploaded_data.columns),
                            'target_column': result.get('target_column')
                        }
                        result['report_generator'].generate_pdf_report(
                            output_path=pdf_path, metrics=result['metrics'],
                            feature_importance=result.get('feature_importance', pd.DataFrame()),
                            task_type=result['task_type'], dataset_info=dataset_info,
                            predictions=result.get('predictions'), df=st.session_state.uploaded_data
                        )
                        with open(pdf_path, 'rb') as f:
                            pdf_data = f.read()
                        st.download_button(
                            label="⬇️ Download PDF Report", data=pdf_data,
                            file_name=f"promptml_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf", width='stretch'
                        )
                        os.unlink(pdf_path)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    with col3:
        if st.button("🔨 Generate Python Package", width='stretch', key="dev_pkg_btn"):
            with st.spinner("Creating package..."):
                try:
                    feature_columns = st.session_state.uploaded_data.drop(columns=[result['target_column']]).columns.tolist()
                    feature_types = infer_types(st.session_state.uploaded_data.drop(columns=[result['target_column']]))
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                        import joblib
                        model_buf = io.BytesIO()
                        joblib.dump(result['model'], model_buf)
                        zf.writestr('model.pkl', model_buf.getvalue())
                        if not result['feature_importance'].empty:
                            zf.writestr('feature_importance.csv', result['feature_importance'].to_csv(index=False))
                        task_type = result['task_type']
                        zf.writestr('predict.py', f'import pandas as pd\nimport joblib\nimport sys\nmodel = joblib.load("model.pkl")\ndf = pd.read_csv(sys.argv[1])\nprint(model.predict(df))\n')
                        zf.writestr('requirements.txt', "pandas\nnumpy\nscikit-learn\npycaret==3.3.2\njoblib\n")
                        zf.writestr('README.md', f"# PromptML Model\nTask: {task_type.title()}\nModel: {metrics.get('model_name','Unknown')}\n\n```bash\npip install -r requirements.txt\npython predict.py your_data.csv\n```\n")
                    zip_buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download Package (ZIP)", data=zip_buffer.getvalue(),
                        file_name=f"promptml_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip", width='stretch'
                    )
                    st.success("✅ Package ready!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
def run_generated_app():
    """Run the generated application preview."""
    if st.session_state.get("preview_html"):
        import streamlit.components.v1 as components
        components.html(st.session_state["preview_html"], height=700, scrolling=True)
    else:
        st.warning("⚠️ Preview not generated. Please build the website first in the 'Deploy as Website' section.")


def deploy_to_cloud():
    """Step-by-step Streamlit Cloud deployment guide."""
    st.markdown("### ☁️ Deploy Your ML App — Free & Live in 2 Minutes")
    st.caption("Streamlit Cloud gives you a **free public URL** — no credit card, no server setup.")
    st.markdown("---")
    with st.expander("✅ Step 1 — Download the Website ZIP", expanded=True):
        st.markdown("""
        - Go back to the **Studio** and click **⬇️ Download Website ZIP**
        - Extract the ZIP — you'll see these files:
        """)
        st.code("""
app.py               ← Your prediction app
model.pkl            ← Trained ML model
requirements.txt     ← Python dependencies
runtime.txt          ← Pins Python 3.11
.python-version      ← Pins Python 3.11 (for uv installer)
README.md            ← Full deploy instructions
        """)
    with st.expander("✅ Step 2 — Push to GitHub (2 mins)", expanded=True):
        st.markdown("""
        1. Go to [github.com](https://github.com) → sign in (or create free account)
        2. Click **+** → **New Repository**
        3. Name it anything (e.g. `my-ml-app`) → set to **Public** → **Create**
        4. Click **Add file → Upload files** → drag all extracted files → **Commit**
        """)
        st.info("💡 No Git or terminal needed — just drag and drop in the browser!")
    with st.expander("✅ Step 3 — Deploy on Streamlit Cloud (1 min)", expanded=True):
        st.markdown("""
        1. Go to [share.streamlit.io](https://share.streamlit.io) → **Sign in with GitHub**
        2. Click **New app**
        3. Select your repo and set **Main file path** to `app.py`
        4. Click **Advanced settings** → set **Python version to 3.11** ⚠️ Mandatory
        5. Click **Deploy!**
        """)
        st.success("🎉 That's it! Your app will be live at a URL like:")
        st.code("https://your-username-my-ml-app-app-xxxxx.streamlit.app")
        st.markdown("Share this link with **anyone** — they can use your model from any device!")
    with st.expander("⚠️ Common Issues & Fixes"):
        st.markdown("""
        | Problem | Fix |
        |---|---|
        | `No module named 'pycaret'` | Advanced settings → Python 3.11 not set. Go to ⋮ → Settings → Advanced → Python 3.11 → Reboot |
        | Build fails on Streamlit Cloud | Make sure all files including `runtime.txt` and `.python-version` are uploaded |
        | `model.pkl` not found error | Re-upload — GitHub sometimes skips large files |
        | App shows dependency error | Don't edit `requirements.txt` — it has all pinned versions |
        | Repo must be Public | Streamlit Cloud free tier only supports public repos |
        """)
        st.markdown("Still stuck? Ask the **PromptML AI Assistant** in the sidebar!")


def show_footer():
    """Footer with working About navigation button styled as a link"""
    
    st.markdown("""
    <style>
    .footer-nav-btn > div > button,
    .footer-nav-btn button {
        background: transparent !important;
        border: none !important;
        color: #888 !important;
        font-size: 0.855rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 400 !important;
        padding: 0px !important;
        margin: 0px !important;
        box-shadow: none !important;
        min-height: 0px !important;
        height: auto !important;
        line-height: 1.5 !important;
        width: auto !important;
        text-decoration: underline !important;
        text-decoration-color: rgba(102,126,234,0.4) !important;
        text-underline-offset: 3px !important;
        border-radius: 0px !important;
        transform: none !important;
    }
    .footer-nav-btn > div > button:hover,
    .footer-nav-btn button:hover {
        color: #c5caff !important;
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        transform: none !important;
        text-decoration-color: #667eea !important;
    }
    .footer-nav-btn > div > button:focus,
    .footer-nav-btn button:focus {
        box-shadow: none !important;
        outline: none !important;
        border: none !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    

    # Footer top bar
    st.markdown('<div class="pml-footer-static">', unsafe_allow_html=True)

    # 4-column footer grid using Streamlit columns
    col_brand, col_platform, col_support, col_resources = st.columns([2, 1, 1, 1])

    with col_brand:
        st.markdown('<div class="pml-footer-logo">🤖 PromptML Studio</div>', unsafe_allow_html=True)
        st.markdown('<div class="pml-footer-tagline">Democratizing AI/ML for everyone.</div>', unsafe_allow_html=True)

    with col_platform:
        st.markdown("""<div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;color:#667eea;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid rgba(102,126,234,0.15);">Platform</div><a style="display:block;font-size:0.82rem;color:#888;text-decoration:none;margin-bottom:6px;font-family:'Inter',sans-serif;cursor:pointer;" href="?nav=about" target="_self">About ›</a><a style="display:block;font-size:0.82rem;color:#888;text-decoration:none;margin-bottom:6px;font-family:'Inter',sans-serif;cursor:pointer;" href="?nav=how_it_works" target="_self">How It Works ›</a><a style="display:block;font-size:0.82rem;color:#888;text-decoration:none;margin-bottom:6px;font-family:'Inter',sans-serif;cursor:pointer;" href="?nav=features" target="_self">Features ›</a>""", unsafe_allow_html=True)


    with col_support:
        st.markdown('<div class="pml-footer-col-title">Support</div>', unsafe_allow_html=True)
        st.markdown('<a style="display:block;font-size:0.82rem;color:#888;text-decoration:none;margin-bottom:6px;font-family:\'Inter\',sans-serif;" href="?nav=contact" target="_self">Contact ›</a>', unsafe_allow_html=True)

    with col_resources:
        st.markdown('<div class="pml-footer-col-title">Resources</div>', unsafe_allow_html=True)
        st.markdown('<a style="display:block;font-size:0.82rem;color:#888;text-decoration:none;margin-bottom:6px;font-family:\'Inter\',sans-serif;" href="https://github.com/Ya3hU4awant/PromptML_Studio" target="_blank">GitHub ›</a>', unsafe_allow_html=True)
        st.markdown('<a style="display:block;font-size:0.82rem;color:#888;text-decoration:none;margin-bottom:6px;font-family:\'Inter\',sans-serif;" href="#">Documentation ›</a>', unsafe_allow_html=True)
        st.markdown('<a style="display:block;font-size:0.82rem;color:#888;text-decoration:none;margin-bottom:6px;font-family:\'Inter\',sans-serif;" href="?nav=privacy" target="_self">Privacy Policy ›</a>', unsafe_allow_html=True)

    st.markdown('<hr class="pml-footer-divider">', unsafe_allow_html=True)
    st.markdown('<div class="pml-footer-copy">© 2026 <span>PromptML Studio</span>. All rights reserved.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():

    # ── SESSION STATE ──────────────────────────────────────────
    if "preview_mode" not in st.session_state:
        st.session_state.preview_mode = False

    # ==============================
    # FULL SCREEN PREVIEW MODE
    # ==============================
    if st.session_state.preview_mode:
        st.markdown("""
            <style>
                header {visibility: hidden;}
                footer {visibility: hidden;}
                .block-container {padding-top: 1rem;}
            </style>
        """, unsafe_allow_html=True)
        run_generated_app()
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅ Back to Studio", use_container_width=True):
                st.session_state.preview_mode = False
                st.rerun()
        with col2:
            if st.button("☁️ Deploy to Streamlit Cloud", use_container_width=True, type="primary"):
                deploy_to_cloud()
        st.stop()

    # Handle footer link navigation via query params
    nav = st.query_params.get("nav", "")
    if nav == "about" and st.session_state.current_page != "about":
        st.session_state.current_page = "about"
        st.query_params.clear()
        st.rerun()
    elif nav == "how_it_works" and st.session_state.current_page != "how_it_works":
        st.session_state.current_page = "how_it_works"
        st.query_params.clear()
        st.rerun()
    elif nav == "features" and st.session_state.current_page != "features":
        st.session_state.current_page = "features"
        st.query_params.clear()
        st.rerun()
    elif nav == "contact" and st.session_state.current_page != "contact":
        st.session_state.current_page = "contact"
        st.query_params.clear()
        st.rerun()
    elif nav == "privacy" and st.session_state.current_page != "privacy":
        st.session_state.current_page = "privacy"
        st.query_params.clear()
        st.rerun()

    elif nav == "" and st.session_state.current_page in ("about", "how_it_works", "features", "contact", "privacy"):
        pass

    # ── SIDEBAR ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🤖 PromptML Assistant")
        st.caption("ML • Data Science • Computer Science • Your Results")

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
Your expertise covers ML, Data Science, Python, and the PromptML Studio platform.
Be friendly, use simple analogies, bullet points, and always end with 1 actionable tip.
{context_block}"""

        # Prompt Refiner
        st.markdown("**✨ Prompt Refiner**")
        user_raw_prompt = st.text_input("Paste your prompt to refine:", placeholder="e.g. predict sales...", key="prompt_refiner_input")
        if st.button("✨ Refine My Prompt", width='stretch', key="refine_btn"):
            if user_raw_prompt.strip():
                refine_q = f"Refine this ML prompt for PromptML Studio. Give 2-3 improved versions: '{user_raw_prompt}'"
                st.session_state.chat_history.append({"role": "user", "content": refine_q})
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", ""))
                    resp = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile", max_tokens=1024,
                        messages=[{"role": "system", "content": system_prompt},
                                  *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history if m["role"] in ("user", "assistant")]]
                    )
                    bot_reply = resp.choices[0].message.content
                except Exception as e:
                    bot_reply = f"⚠️ Groq error: {e}"
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                st.rerun()

        # FAQs
        faq_options = {
            "— Select a question —": "",
            "📌 How do I use PromptML Studio?": "Explain how to use PromptML Studio step by step in simple non-technical terms",
            "📌 Why is my dataset not working?": "Why might my CSV dataset not work in PromptML Studio and how do I fix it?",
            "📌 Why are my results so low?": "My model results are very low, what could be wrong and how do I improve them?",
            "📌 What is Accuracy?": "Explain Accuracy in machine learning in very simple terms with a real life example",
            "📌 What is R² score?": "Explain R² score in very simple terms with a real life example",
            "📌 What is RMSE?": "Explain RMSE in very simple terms with a real life example",
            "📌 What is feature importance?": "Explain feature importance in simple terms, why does it matter?",
            "📌 No-Code vs Developer Mode?": "What is the difference between No-Code Mode and Developer Mode in PromptML Studio?",
            "📌 How to improve my model?": "Give me simple practical tips to improve my machine learning model results",
            "📌 What is overfitting?": "Explain overfitting in very simple non-technical terms with a real life example",
        }
        selected_faq = st.selectbox("💡 FAQs & Quick Questions", options=list(faq_options.keys()), key="faq_select")
        if selected_faq != "— Select a question —":
            if st.button("Ask this ➤", width='stretch', key="faq_btn"):
                question = faq_options[selected_faq]
                st.session_state.chat_history.append({"role": "user", "content": question})
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", ""))
                    resp = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile", max_tokens=1024,
                        messages=[{"role": "system", "content": system_prompt},
                                  *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history if m["role"] in ("user", "assistant")]]
                    )
                    bot_reply = resp.choices[0].message.content
                except Exception as e:
                    bot_reply = f"⚠️ Groq error: {e}"
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                st.rerun()

        user_input = st.text_input("Ask me anything...", placeholder="e.g. What is Random Forest?", key="chat_input")
        send_col, clear_col = st.columns([2, 1])
        send_clicked  = send_col.button("Send ➤", width='stretch', type="primary")
        clear_clicked = clear_col.button("🗑️ Clear", width='stretch')
        if clear_clicked:
            st.session_state.chat_history = []
            st.rerun()
        if send_clicked and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
            try:
                from groq import Groq
                groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", ""))
                resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile", max_tokens=1024,
                    messages=[{"role": "system", "content": system_prompt},
                              *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history if m["role"] in ("user", "assistant")]]
                )
                bot_reply = resp.choices[0].message.content
            except Exception as e:
                bot_reply = f"⚠️ Groq API error: {e}"
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            st.rerun()
        st.markdown("---")
        for msg in reversed(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(f"<div style='background:#1e1e2e;padding:8px 12px;border-radius:8px;margin-bottom:6px;border-left:3px solid #6c63ff'>🧑 <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                content = msg['content'].replace(">>", "&rsaquo;&rsaquo;&rsaquo;")
                st.markdown(f"<div style='background:#0f2a1a;padding:8px 12px;border-radius:8px;margin-bottom:10px;border-left:3px solid #2ecc71'>🤖 <b>Assistant:</b><br>{content}</div>", unsafe_allow_html=True)

        st.markdown("---")
        if st.session_state.mode:
            mode_emoji = "📱" if st.session_state.mode == "no-code" else "💻"
            st.info(f"{mode_emoji} **{st.session_state.mode.title()} Mode**")
            if st.button("🔄 Change Mode"):
                st.session_state.mode = None
                st.session_state.model_trained = False
                st.session_state.model_result = None
                st.rerun()
        st.markdown("---")

    # ── MAIN CONTENT — PAGE ROUTER ────────────────────────────
    if st.session_state.current_page == "about":
        show_about_page()

    elif st.session_state.current_page == "how_it_works":
        show_how_it_works_page()

    elif st.session_state.current_page == "features":
        show_features_page()
    
    elif st.session_state.current_page == "contact":
        show_contact_page()

    elif st.session_state.current_page == "privacy":
        show_privacy_page()

    elif st.session_state.mode is None:
        show_hero_section()
        show_mode_selector()

    else:
        st.title(f"{'📱 No-Code' if st.session_state.mode == 'no-code' else '💻 Developer'} Mode")
        df = upload_data_section()
        if df is not None:
            prompt = prompt_input_section()
            if prompt:
                train_model_section(df, prompt)
                if st.session_state.mode == "no-code":
                    show_results_no_code()
                else:
                    show_results_developer()

                from backend.ml_engine.website_generator import generate_website, generate_preview_html
                if st.session_state.get("model_trained"):
                    st.markdown("---")
                    st.subheader("🌍 Deploy as Website")
                    if st.button("🚀 Build Website", type="primary", width='stretch'):
                        with st.spinner("Generating website..."):
                            zip_path = generate_website()
                            st.session_state["website_zip_path"] = zip_path
                            import joblib as _jl
                            _features = _jl.load("artifacts/features.pkl")
                            _task_type = _jl.load("artifacts/task_type.pkl")
                            st.session_state["preview_html"] = generate_preview_html(_features, _task_type)
                    if st.session_state.get("website_zip_path"):
                        st.success("✅ Website generated successfully!")
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            with open(st.session_state["website_zip_path"], "rb") as f:
                                st.download_button("⬇️ Download Website ZIP", f, file_name="promptml_website.zip", mime="application/zip", width='stretch')
                        with btn_col2:
                            if st.button("👁️ Preview / Deploy", width='stretch'):
                                st.session_state.preview_mode = True
                                st.rerun()

    # ── FOOTER — always at bottom ─────────────────────────────
    show_footer()


if __name__ == "__main__":
    main()