# 🚀 PromptML Studio: AI-Powered ML Model Builder

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PromptML Studio** is an AI-powered AutoML platform that democratizes machine learning. Upload a CSV, describe your goal in natural language, and get production-ready ML models instantly!

## 🎯 Project Overview

**Title**: PromptML Studio: AI-Powered ML Model Builder with Dual-Mode Interface  
**Target**: 6-month AIML diploma final year project, deployable demo for MNC interviews  
**Live Demo**: [Your Render.com URL]

### Key Features

✨ **Dual-Mode Interface**:
- 🎨 **No-Code Mode**: Drag-drop CSV → Interactive charts + PDF reports
- 💻 **Developer Mode**: Complete Python package ZIP (model.pkl + editable code)

🤖 **AI-Powered**:
- Natural language prompt parsing
- Automatic task detection (regression/classification)
- Auto-selects best ML algorithm from 10+ models

📊 **Professional Outputs**:
- Interactive Plotly visualizations
- Comprehensive PDF reports
- Production-ready Python packages
- New data predictions

## 🏗️ Technology Stack

- **Frontend**: Streamlit + Bootstrap 5
- **AutoML**: PyCaret, scikit-learn, XGBoost
- **Deep Learning**: TensorFlow/Keras
- **NLP**: OpenAI API / HuggingFace
- **Visualization**: Plotly, Matplotlib
- **Export**: WeasyPrint (PDF), zipfile
- **Deployment**: Docker + Render/Railway ready

## 📋 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8 or higher
- pip or conda

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd PromptML_Studio
```

2. **Create virtual environment**
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# OR using conda
conda create -n promptml python=3.8
conda activate promptml
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open your browser**
Navigate to `http://localhost:8501`

## 🎮 User Workflow

1. **Select Mode**: Choose between No-Code or Developer mode
2. **Upload CSV**: Drag-drop your dataset
3. **Enter Prompt**: Describe your goal (e.g., "Predict house prices")
4. **AI Processing**: 
   - Parses prompt to detect task type
   - Auto-preprocesses data
   - Trains 10+ models
   - Selects best performer
5. **Get Results**:
   - **No-Code**: Interactive charts + PDF report + predictions
   - **Developer**: ZIP package with model + complete code

## 📁 Project Structure

```
PromptML_Studio/
├── app.py                      # Main Streamlit application
├── backend/
│   ├── __init__.py
│   ├── ml_engine/
│   │   ├── __init__.py
│   │   ├── prompt_parser.py    # NLP prompt parsing
│   │   ├── model_builder.py    # PyCaret AutoML pipeline
│   │   └── report_generator.py # PDF + chart generation
│   └── predictor.py            # Prediction engine
├── static/
│   ├── style.css               # Custom styling
│   └── sample_data/            # Sample datasets
│       ├── house_prices.csv
│       └── customer_churn.csv
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

## 🚀 Deployment to Render.com

### Step 1: Prepare Your Repository
```bash
git init
git add .
git commit -m "Initial commit: PromptML Studio"
git remote add origin <your-github-repo>
git push -u origin main
```

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: promptml-studio
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Click "Create Web Service"
6. Wait 5-10 minutes for deployment

### Step 3: Access Your App
Your app will be live at: `https://promptml-studio.onrender.com`

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t promptml-studio .
```

### Run Container
```bash
docker run -p 8501:8501 promptml-studio
```

Access at `http://localhost:8501`

## 📊 Sample Datasets

The application includes two sample datasets:

### 1. House Prices (Regression)
- **Features**: bedrooms, bathrooms, sqft_living, sqft_lot, floors, etc.
- **Target**: price
- **Prompt Example**: "Predict house prices based on features"

### 2. Customer Churn (Classification)
- **Features**: tenure, monthly_charges, contract_type, payment_method, etc.
- **Target**: churn
- **Prompt Example**: "Classify customer churn risk"

## 🎨 Features Showcase

### No-Code Mode
- ✅ Drag-drop CSV upload
- ✅ Automatic data preview
- ✅ Model performance metrics (Accuracy, F1, RMSE, R²)
- ✅ Interactive training curves
- ✅ Feature importance charts
- ✅ Confusion matrix (classification)
- ✅ Downloadable PDF report
- ✅ New data prediction interface

### Developer Mode
- ✅ Complete Python package ZIP
- ✅ Trained model files (model.pkl, preprocessor.pkl)
- ✅ Production-ready scripts (ml_pipeline.py, predict.py)
- ✅ requirements.txt
- ✅ Unit tests
- ✅ Full documentation

## 🧪 Testing

### Test with Sample Data
1. Launch the app
2. Select "No-Code Mode"
3. Upload `static/sample_data/house_prices.csv`
4. Enter prompt: "Predict house prices"
5. Wait 30-60 seconds
6. Review results and download report

### Test Developer Mode
1. Select "Developer Mode"
2. Upload dataset
3. Enter prompt
4. Download ZIP package
5. Extract and run:
```bash
cd extracted_package
pip install -r requirements.txt
python predict.py new_data.csv
```

## 🎓 AIML Diploma Project Presentation Tips

### Key Points to Highlight
1. **Innovation**: Natural language → Production ML (no coding required)
2. **Dual Audience**: Serves both business users AND developers
3. **AutoML**: Compares 10+ algorithms automatically
4. **Production-Ready**: Exports complete, deployable code
5. **Real-World Impact**: Democratizes AI/ML for non-technical users

### Demo Flow (5 minutes)
1. Show landing page (30 sec)
2. Upload CSV + prompt (30 sec)
3. Show AI processing (1 min)
4. Present results: charts + metrics (2 min)
5. Download outputs (1 min)
6. Show deployed live demo (30 sec)

## 🛠️ Customization

### Add Custom Models
Edit `backend/ml_engine/model_builder.py`:
```python
# Add your custom model to the comparison
from sklearn.ensemble import YourCustomModel
# PyCaret will automatically include it
```

### Modify UI Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#your-color"
backgroundColor = "#your-bg"
```

### Add New Prompt Patterns
Edit `backend/ml_engine/prompt_parser.py`:
```python
# Add new keywords for task detection
REGRESSION_KEYWORDS = ['predict', 'forecast', 'estimate', 'your-keyword']
```

## 📈 Performance Benchmarks

- **CSV Upload**: < 2 seconds
- **Model Training**: 30-90 seconds (depends on dataset size)
- **Report Generation**: 5-10 seconds
- **Prediction**: < 1 second per row

## 🤝 Contributing

This is an academic project, but contributions are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Your Name**  
AIML Diploma Final Year Project  
[Your Email] | [LinkedIn] | [GitHub]

## 🙏 Acknowledgments

- PyCaret for AutoML capabilities
- Streamlit for rapid UI development
- scikit-learn, XGBoost for ML algorithms
- OpenAI/HuggingFace for NLP

## 📞 Support

For issues or questions:
- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](your-repo-url/issues)
- 💬 Discussions: [GitHub Discussions](your-repo-url/discussions)

---

⭐ **Star this repo if it helped your AIML project!** ⭐

Made with ❤️ for democratizing AI/ML
