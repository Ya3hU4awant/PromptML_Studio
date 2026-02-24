# 🚀 Deployment Guide - PromptML Studio

This guide will help you deploy PromptML Studio to various platforms.

## 📋 Prerequisites

- Git installed
- GitHub account
- Python 3.8+ installed locally

## 🌐 Option 1: Deploy to Render.com (Recommended)

Render.com offers free hosting for web applications with automatic deployments.

### Step 1: Prepare Your Repository

```bash
# Navigate to project directory
cd PromptML_Studio

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: PromptML Studio"

# Create GitHub repository and push
# (Create a new repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/promptml-studio.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account and select your repository
4. Configure the service:
   - **Name**: `promptml-studio`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment
7. Your app will be live at: `https://promptml-studio.onrender.com`

### Important Notes for Render:
- Free tier may spin down after inactivity
- First load after inactivity may take 30-60 seconds
- Upgrade to paid tier for always-on service

## 🚂 Option 2: Deploy to Railway.app

Railway offers simple deployment with generous free tier.

### Step 1: Prepare Repository
(Same as Render - push to GitHub)

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign up
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect Python and deploy
5. Add environment variable:
   - Key: `PORT`
   - Value: `8501`
6. Your app will be live at: `https://your-app.railway.app`

## 🐳 Option 3: Deploy with Docker

### Local Docker Deployment

```bash
# Build Docker image
docker build -t promptml-studio .

# Run container
docker run -p 8501:8501 promptml-studio

# Access at http://localhost:8501
```

### Deploy to Docker Hub

```bash
# Tag image
docker tag promptml-studio YOUR_USERNAME/promptml-studio:latest

# Push to Docker Hub
docker push YOUR_USERNAME/promptml-studio:latest

# Others can now run:
docker pull YOUR_USERNAME/promptml-studio:latest
docker run -p 8501:8501 YOUR_USERNAME/promptml-studio:latest
```

## ☁️ Option 4: Deploy to Streamlit Cloud

Streamlit Cloud offers free hosting specifically for Streamlit apps.

### Steps:

1. Push code to GitHub (public repository)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your repository, branch, and `app.py`
5. Click **"Deploy"**
6. Your app will be live at: `https://share.streamlit.io/YOUR_USERNAME/promptml-studio/main/app.py`

### Note:
- Streamlit Cloud has resource limitations
- May need to reduce model complexity for free tier

## 🔧 Option 5: Deploy to Heroku

### Prerequisites:
- Heroku account
- Heroku CLI installed

### Steps:

1. Create `Procfile`:
```bash
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Create `runtime.txt`:
```
python-3.8.18
```

3. Deploy:
```bash
# Login to Heroku
heroku login

# Create app
heroku create promptml-studio

# Push to Heroku
git push heroku main

# Open app
heroku open
```

## 🖥️ Option 6: Local Development Server

For testing and development:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py

# Access at http://localhost:8501
```

## 🔐 Environment Variables (Optional)

If you plan to add OpenAI API or other services:

Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

On Render/Railway, add as environment variables in dashboard.

## 📊 Performance Optimization

### For Production Deployment:

1. **Reduce Model Complexity**:
   - In `model_builder.py`, reduce `n_models` parameter
   - Use faster algorithms for initial comparison

2. **Add Caching**:
   ```python
   @st.cache_data
   def load_data(file):
       return pd.read_csv(file)
   ```

3. **Optimize Memory**:
   - Clear session state when not needed
   - Use smaller datasets for demos

4. **Add Loading States**:
   - Already implemented with progress bars
   - Consider adding more granular feedback

## 🐛 Troubleshooting

### Issue: App crashes on deployment
**Solution**: Check logs for memory issues. Reduce model complexity or upgrade to paid tier.

### Issue: Slow model training
**Solution**: Use smaller datasets or reduce number of models to compare.

### Issue: Import errors
**Solution**: Ensure all dependencies in `requirements.txt` are compatible.

### Issue: Port binding errors
**Solution**: Ensure start command uses `$PORT` environment variable.

## 📈 Monitoring

### Render.com:
- View logs in dashboard
- Set up health checks
- Monitor resource usage

### Railway:
- Real-time logs in dashboard
- Automatic metrics
- Usage analytics

## 🎓 For AIML Diploma Presentation

### Recommended Deployment:
1. **Primary**: Render.com (free, reliable, good for demos)
2. **Backup**: Streamlit Cloud (if Render has issues)
3. **Local**: Docker (for offline presentations)

### Demo Checklist:
- [ ] App deployed and accessible
- [ ] Sample data loads correctly
- [ ] Model training works (test before presentation)
- [ ] PDF generation works
- [ ] Package download works
- [ ] Have backup local version ready

## 📞 Support

If you encounter issues:
1. Check deployment platform logs
2. Verify all dependencies are installed
3. Test locally first
4. Check platform status pages

---

**Good luck with your deployment! 🚀**

For questions or issues, refer to:
- [Streamlit Docs](https://docs.streamlit.io)
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
