"""
PromptML Studio - Main Streamlit Application
AI-Powered AutoML Platform with Dual-Mode Interface
"""
import requests

import shutil
import streamlit as st
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




# Page configuration
st.set_page_config(
    page_title="PromptML Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS styling"""
    css_path = Path(__file__).parent / "static" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
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
    
    st.markdown("---")
    st.markdown("## 📊 Model Results")
    
    # Metrics
    st.markdown("### 🎯 Performance Metrics")
    
    metrics = result['metrics']
    
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
    
    else:  # regression
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("R² Score", f"{metrics.get('r2_score', 0):.4f}")
        with col2:
            st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}")
        with col3:
            st.metric("MAE", f"{metrics.get('mae', 0):.2f}")
        with col4:
            st.metric("MSE", f"{metrics.get('mse', 0):.2f}")
    
    # Model info
    st.info(f"🤖 Best Model: **{metrics.get('model_name', 'Unknown')}**")
    
    # Visualizations
    st.markdown("### 📈 Visualizations")
    
    charts = result['charts']
    
    # Feature importance
    if 'feature_importance' in charts:
        st.plotly_chart(charts['feature_importance'], use_container_width=True)
    
    # Task-specific charts
    if result['task_type'] == 'classification':
        col1, col2 = st.columns(2)
        
        with col1:
            if 'confusion_matrix' in charts:
                st.plotly_chart(charts['confusion_matrix'], use_container_width=True)
        
        with col2:
            if 'metrics_comparison' in charts:
                st.plotly_chart(charts['metrics_comparison'], use_container_width=True)
    
    else:  # regression
        col1, col2 = st.columns(2)
        
        with col1:
            if 'actual_vs_predicted' in charts:
                st.plotly_chart(charts['actual_vs_predicted'], use_container_width=True)
        
        with col2:
            if 'residuals' in charts:
                st.plotly_chart(charts['residuals'], use_container_width=True)
    
    # Model comparison
    if 'comparison' in result and not result['comparison'].empty:
        with st.expander("📊 Model Comparison", expanded=False):
            st.dataframe(result['comparison'], use_container_width=True)
    
    # Download section
    st.markdown("### 📥 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate PDF
        if st.button("📄 Generate PDF Report", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                try:
                    # Create temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        pdf_path = tmp_file.name
                    
                    # Generate PDF
                    dataset_info = {
                        'n_samples': len(st.session_state.uploaded_data),
                        'n_features': len(st.session_state.uploaded_data.columns) - 1,
                        'target_column': result['target_column']
                    }
                    
                    result['report_generator'].generate_pdf_report(
                        output_path=pdf_path,
                        metrics=result['metrics'],
                        feature_importance=result['feature_importance'],
                        task_type=result['task_type'],
                        dataset_info=dataset_info
                    )
                    
                    # Read PDF
                    with open(pdf_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_data,
                        file_name=f"promptml_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Cleanup
                    os.unlink(pdf_path)
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        # Download predictions
        predictions_csv = result['predictions'].to_csv(index=False)
        st.download_button(
            label="📊 Download Predictions CSV",
            data=predictions_csv,
            file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )


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
        st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
    else:
        st.metric("R² Score", f"{metrics.get('r2_score', 0):.4f}")

    # Generate package
    st.markdown("### 📦 Production Package")
    
    # Get feature columns and types
    feature_columns = st.session_state.uploaded_data.drop(columns=[result['target_column']]).columns.tolist()
    feature_types = infer_types(st.session_state.uploaded_data.drop(columns=[result['target_column']]))
    sample_data = st.session_state.uploaded_data.drop(columns=[result['target_column']])
    
    # Generate template
    app_template = generate_app_template(feature_columns, feature_types, sample_data)
    
    if st.button("🔨 Generate Python Package", type="primary", use_container_width=True):
        with st.spinner("Creating production package..."):
            try:
                # Create ZIP file
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Save model
                    import joblib
                    model_buffer = io.BytesIO()
                    joblib.dump(result['model'], model_buffer)
                    zip_file.writestr('model.pkl', model_buffer.getvalue())
                    
                    # Save metrics
                    metrics_buffer = io.BytesIO()
                    joblib.dump(result['metrics'], metrics_buffer)
                    zip_file.writestr('metrics.pkl', metrics_buffer.getvalue())
                    
                    # Save feature importance
                    if not result['feature_importance'].empty:
                        fi_csv = result['feature_importance'].to_csv(index=False)
                        zip_file.writestr('feature_importance.csv', fi_csv)
                    
                    # Create predict.py script
                    task_type = result['task_type']
                    predict_script = f'''"""
Prediction Script for PromptML Studio Model
Task Type: {task_type}
"""

import pandas as pd
import joblib
import sys

def load_model(model_path='model.pkl'):
    """Load trained model"""
    return joblib.load(model_path)

def predict(model, data_path):
    """Make predictions on new data"""
    # Load data
    df = pd.read_csv(data_path)
    
    # Make predictions
    try:
        from pycaret.{task_type} import predict_model
        predictions = predict_model(model, data=df)
    except:
        # Fallback to sklearn
        predictions = model.predict(df)
        df['prediction'] = predictions
        predictions = df
    
    return predictions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <data.csv>")
        sys.exit(1)
    
    # Load model
    model = load_model()
    
    # Make predictions
    predictions = predict(model, sys.argv[1])
    
    # Save results
    output_path = "predictions_output.csv"
    predictions.to_csv(output_path, index=False)
    
    print(f"Predictions saved to {{output_path}}")
    print(f"Predicted {{len(predictions)}} samples")
'''
                    zip_file.writestr('predict.py', predict_script)
                    
                    # Create requirements.txt
                    requirements = "pandas==2.0.3\nnumpy==1.24.3\nscikit-learn==1.3.0\npycaret==3.1.0\njoblib==1.3.2\n"
                    zip_file.writestr('requirements.txt', requirements)
                    
                    # Create README
                    task_type_title = result['task_type'].title()
                    model_name = metrics.get('model_name', 'Unknown')
                    gen_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    readme = f"# PromptML Studio - Production Model Package\n\n## Model Information\n- **Task Type**: {task_type_title}\n- **Model**: {model_name}\n- **Generated**: {gen_time}\n\n## Performance Metrics\n"
                    
                    if result['task_type'] == 'classification':
                        accuracy = metrics.get('accuracy', 0)
                        precision = metrics.get('precision', 0)
                        recall = metrics.get('recall', 0)
                        f1 = metrics.get('f1_score', 0)
                        readme += f"- Accuracy: {accuracy:.2%}\n- Precision: {precision:.2%}\n- Recall: {recall:.2%}\n- F1 Score: {f1:.2%}\n"
                    else:
                        r2 = metrics.get('r2_score', 0)
                        rmse = metrics.get('rmse', 0)
                        mae = metrics.get('mae', 0)
                        readme += f"- R2 Score: {r2:.4f}\n- RMSE: {rmse:.4f}\n- MAE: {mae:.4f}\n"
                    
                    readme += "\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n### Make Predictions\n\n```bash\npython predict.py your_data.csv\n```\n\n### Load Model in Python\n\n```python\nimport joblib\nmodel = joblib.load('model.pkl')\n```\n\n## Files Included\n- `model.pkl` - Trained model\n- `metrics.pkl` - Performance metrics\n- `feature_importance.csv` - Feature importance scores\n- `predict.py` - Prediction script\n- `requirements.txt` - Python dependencies\n- `README.md` - This file\n\n---\nGenerated by PromptML Studio\n"
                    zip_file.writestr('README.md', readme)
                
                # Download button
                zip_buffer.seek(0)
                st.download_button(
                    label="⬇️ Download Complete Package (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"promptml_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                st.success("✅ Package created successfully!")
                
                # Show package contents
                with st.expander("📦 Package Contents"):
                    st.markdown("""
                    - `model.pkl` - Trained model file
                    - `metrics.pkl` - Performance metrics
                    - `feature_importance.csv` - Feature importance
                    - `predict.py` - Ready-to-use prediction script
                    - `requirements.txt` - Python dependencies
                    - `README.md` - Documentation
                    """)
                
            except Exception as e:
                st.error(f"Error creating package: {str(e)}")
                st.exception(e)


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
        st.title("PromptML Studio")
        st.markdown("---")
        
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

                from backend.ml_engine.website_generator import generate_website

                if st.session_state.get("model_trained"):
                    st.markdown("---")
                    st.subheader("🌍 Deploy as Website")

                    if st.button("🚀 Build Website", type="primary", use_container_width=True):
                        with st.spinner("Generating website..."):
                            zip_path = generate_website()
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    "⬇️ Download Website ZIP",
                                    f,
                                    file_name="promptml_website.zip",
                                    mime="application/zip"
                                )
                            st.success("Website generated successfully!")
    

            

                # ===== NLP API SECTION =====
                st.markdown("## 🔍 NLP Text Analysis")

                text_input = st.text_area(
                    "Enter your text",
                    placeholder="I love PromptML project"
                )

                if st.button("Analyze"):
                    if not text_input.strip():
                        st.warning("Please enter text")
                    else:
                        try:
                            response = requests.post(
                                "http://127.0.0.1:8000/predict",
                                json={"text": text_input},
                                timeout=5
                            )

                            st.write("DEBUG status:", response.status_code)

                            if response.status_code == 200:
                                
                                

                                result = response.json()
                                st.success("Analysis Result 👇")
                                st.write("Text:", result["text"])
                                st.write("Label:",result["label"])
                                st.write("Confidence:", result["confidence"])
                                
                        
                            
                            

                                label = result.get("label")
                                conf = result.get("confidence", 0)

                                st.success("Done ✅")

                                if conf >= 0.6:
                                    st.write("**Label:**", label)
                                else:
                                    st.write("**Label:** UNCERTAIN")

                                    st.write("**Confidence:**", f"{conf*100:.2f}%")

                                if conf < 0.6:
                                    st.warning("Neutral / Confused 😐")
                                elif label == "POSITIVE":
                                    st.success("Positive Sentiment 😊")
                                elif label == "NEGATIVE":
                                    st.error("Negative Sentiment 😞")
                                else:
                                    st.warning("Neutral / Uncertain Sentiment 🤔")
                            else:
                                st.error("API Error")
            
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Backend API running nahi hai (FastAPI start karo)")

                        except requests.exceptions.Timeout:
                            st.error("⏳ API response slow hai, thodi der baad try karo")

                        except Exception as e:
                            print(traceback.format_exc)
                            st.error(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
