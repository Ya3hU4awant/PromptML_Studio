"""
PromptML Studio - Main Streamlit Application
AI-Powered AutoML Platform with Dual-Mode Interface
"""

import streamlit as st
import pandas as pd
import joblib
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
from backend.ml_engine.model_builder import save_trained_model
from backend.ml_engine.website_generator import generate_website


# Add backend to path
sys.path.append(str(Path(__file__).parent))

from backend.ml_engine.prompt_parser import PromptParser
from backend.ml_engine.model_builder import ModelBuilder
from backend.ml_engine.report_generator import ReportGenerator
from backend.predictor import Predictor

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
        if st.button("📱 No-Code Mode", use_container_width=True, type="primary"):
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
        if st.button("💻 Developer Mode", use_container_width=True, type="secondary"):
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
        if st.button("📝 Use House Prices Sample", use_container_width=True):
            sample_path = Path(__file__).parent / "static" / "sample_data" / "house_prices.csv"
            if sample_path.exists():
                st.session_state.uploaded_data = pd.read_csv(sample_path)
                st.session_state.sample_prompt = "Predict house prices based on features"
                st.success("✅ House prices sample data loaded!")
                st.rerun()
    
    with col2:
        if st.button("📝 Use Customer Churn Sample", use_container_width=True):
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
                st.dataframe(df.head(10), use_container_width=True)
                
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
            st.dataframe(df.head(10), use_container_width=True)
    
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
                    predict_script = f"""                   
Prediction Script for PromptML Studio Model
Task Type: {result['task_type']}


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
        from pycaret.{result['task_type']} import predict_model
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
    
    print(f"✅ Predictions saved to {{output_path}}")
    print(f"📊 Predicted {{len(predictions)}} samples")
'''
                    zip_file.writestr('predict.py', predict_script)
                    
                    # Create requirements.txt
                    requirements = '''pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
pycaret==3.1.0
joblib==1.3.2
'''
                    zip_file.writestr('requirements.txt', requirements)
                    
                    # Create README
                    readme = f'''# PromptML Studio - Production Model Package

## Model Information
- **Task Type**: {result['task_type'].title()}
- **Model**: {metrics.get('model_name', 'Unknown')}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Performance Metrics
'''
                    if result['task_type'] == 'classification':
                        readme += f'''- Accuracy: {metrics.get('accuracy', 0):.2%}
- Precision: {metrics.get('precision', 0):.2%}
- Recall: {metrics.get('recall', 0):.2%}
- F1 Score: {metrics.get('f1_score', 0):.2%}
'''
                    else:
                        readme += f'''- R² Score: {metrics.get('r2_score', 0):.4f}
- RMSE: {metrics.get('rmse', 0):.4f}
- MAE: {metrics.get('mae', 0):.4f}
'''
                    
                    readme += '''
## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Make Predictions

```bash
python predict.py your_data.csv
```

### Load Model in Python

```python
import joblib
model = joblib.load('model.pkl')
```

## Files Included
- `model.pkl` - Trained model
- `metrics.pkl` - Performance metrics
- `feature_importance.csv` - Feature importance scores
- `predict.py` - Prediction script
- `requirements.txt` - Python dependencies
- `README.md` - This file

---
Generated by PromptML Studio
'''
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


if __name__ == "__main__":
    main()
"""    

# ===============================
# WEBSITE GENERATION SECTION
# ===============================

if st.session_state.get("model_trained", False):

    st.markdown("---")
    st.subheader("🌍 Deploy this Model as a Website")

    if st.button("🚀 Build Website using this Model", use_container_width=True):
        with st.spinner("Generating website for your trained model..."):

            save_trained_model(
                st.session_state.model_result["model"]
            )
            output_dir = "generated_website"

            zip_path = generate_website(
                output_dir=output_dir,
                task_type=st.session_state.model_result["task_type"],
                target_column=st.session_state.model_result["target_column"],
                model=st.session_state.model_result["model"]
            )


            with open(zip_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Website ZIP",
                    f,
                    file_name="ml_model_website.zip",
                    mime="application/zip"
                )

            st.success("✅ Website generated successfully!")
