"""
PromptML Studio - Features Page
"""
import streamlit as st


def show_features_page():
    """Render the Features page"""

    def go_home():
        st.session_state.current_page = "home"
        st.session_state.mode = None
        st.query_params.clear()
        st.rerun()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
    .feat-hero { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); border-radius: 16px; padding: 56px 48px; text-align: center; margin-bottom: 36px; position: relative; overflow: hidden; }
    .feat-hero-label { font-family: 'Inter', sans-serif; font-size: 0.72rem; font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase; color: #8899ee; margin-bottom: 14px; }
    .feat-hero-title { font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 30%, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 18px; line-height: 1.15; }
    .feat-hero-sub { font-family: 'Inter', sans-serif; font-size: 1rem; color: rgba(255,255,255,0.6); max-width: 560px; margin: 0 auto; line-height: 1.7; }
    .feat-section-title { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 6px; margin-top: 8px; }
    .feat-section-line { width: 44px; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 2px; margin-bottom: 24px; }
    .feat-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 36px; }
    .feat-stat { background: #13132a; border: 1px solid rgba(102,126,234,0.12); border-radius: 12px; padding: 18px 16px; text-align: center; }
    .feat-stat-num { font-family: 'Outfit', sans-serif; font-size: 1.7rem; font-weight: 800; background: linear-gradient(135deg, #667eea, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1; margin-bottom: 5px; }
    .feat-stat-label { font-family: 'Inter', sans-serif; font-size: 0.72rem; color: #555; text-transform: uppercase; letter-spacing: 0.8px; }
    .feat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 36px; }
    .feat-card { background: #13132a; border: 1px solid rgba(102,126,234,0.12); border-radius: 12px; padding: 22px 18px; position: relative; }
    .feat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 12px 12px 0 0; opacity: 0.6; }
    .feat-icon { font-size: 1.6rem; margin-bottom: 10px; }
    .feat-title { font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 600; color: #ddd; margin-bottom: 7px; }
    .feat-desc { font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #666; line-height: 1.65; }
    .feat-badge { display: inline-block; margin-top: 10px; padding: 2px 10px; border-radius: 20px; font-size: 0.68rem; font-family: 'Inter', sans-serif; font-weight: 500; background: rgba(102,126,234,0.1); border: 1px solid rgba(102,126,234,0.2); color: #8899ee; }
    .deploy-header { background: linear-gradient(135deg, rgba(17,153,142,0.1), rgba(56,239,125,0.06)); border: 1px solid rgba(17,153,142,0.2); border-radius: 12px; padding: 18px 24px; margin-bottom: 24px; display: flex; align-items: center; gap: 14px; }
    .deploy-header-icon { font-size: 1.8rem; }
    .deploy-header-title { font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: #fff; }
    .deploy-header-sub { font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #888; margin-top: 2px; }
    .deploy-steps { display: flex; flex-direction: column; gap: 12px; margin-bottom: 28px; }
    .deploy-step { background: #16162a; border: 1px solid rgba(17,153,142,0.15); border-radius: 12px; padding: 18px 20px; display: flex; gap: 16px; align-items: flex-start; }
    .deploy-num { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #11998e, #38ef7d); display: flex; align-items: center; justify-content: center; font-family: 'Outfit', sans-serif; font-size: 0.85rem; font-weight: 700; color: #fff; flex-shrink: 0; margin-top: 2px; }
    .deploy-step-title { font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 600; color: #ddd; margin-bottom: 4px; }
    .deploy-step-desc { font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #777; line-height: 1.6; }
    .code-pill { display: inline-block; background: rgba(167,139,250,0.1); color: #a78bfa; font-family: 'Courier New', monospace; font-size: 0.78rem; padding: 2px 8px; border-radius: 5px; margin: 2px 2px 0 0; }
    .deploy-tip { display: inline-block; margin-top: 7px; font-family: 'Inter', sans-serif; font-size: 0.76rem; color: #38ef7d; background: rgba(56,239,125,0.08); border-radius: 6px; padding: 3px 10px; }
    .platform-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 28px; }
    .platform-card { background: #13132a; border: 1px solid rgba(102,126,234,0.12); border-radius: 12px; padding: 20px 16px; text-align: center; }
    .platform-icon { font-size: 1.8rem; margin-bottom: 8px; }
    .platform-name { font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 700; color: #ddd; margin-bottom: 6px; }
    .platform-desc { font-family: 'Inter', sans-serif; font-size: 0.78rem; color: #666; line-height: 1.5; margin-bottom: 10px; }
    .platform-free { font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; background: rgba(56,239,125,0.1); border: 1px solid rgba(56,239,125,0.25); color: #38ef7d; }
    .tip-box { background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.05)); border: 1px solid rgba(102,126,234,0.2); border-left: 3px solid #667eea; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px; font-family: 'Inter', sans-serif; font-size: 0.84rem; color: #b0b0c8; line-height: 1.7; }
    .tip-box strong { color: #c5caff; }
    div[data-testid="stButton"].back-btn > button { background: rgba(102,126,234,0.1) !important; border: 1px solid rgba(102,126,234,0.3) !important; color: #8899ee !important; font-size: 0.85rem !important; font-family: 'Inter', sans-serif !important; border-radius: 8px !important; padding: 6px 16px !important; }
    div[data-testid="stButton"].back-btn > button:hover { background: rgba(102,126,234,0.2) !important; color: #c5caff !important; transform: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Back button top
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="feat_back_top"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Hero
    st.markdown('<div class="feat-hero"><div class="feat-hero-label">Platform Features</div><div class="feat-hero-title">Everything in One Place</div><div class="feat-hero-sub">From raw CSV to deployed web app — every feature you need to build, understand, and ship machine learning models.</div></div>', unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="feat-stats"><div class="feat-stat"><div class="feat-stat-num">15+</div><div class="feat-stat-label">Algorithms</div></div><div class="feat-stat"><div class="feat-stat-num">7</div><div class="feat-stat-label">Report Sections</div></div><div class="feat-stat"><div class="feat-stat-num">3</div><div class="feat-stat-label">Task Types</div></div><div class="feat-stat"><div class="feat-stat-num">0</div><div class="feat-stat-label">Code Required</div></div></div>', unsafe_allow_html=True)

    # Section 1 — Core Features
    st.markdown('<div class="feat-section-title">Core Features</div>', unsafe_allow_html=True)
    st.markdown('<div class="feat-section-line"></div>', unsafe_allow_html=True)

    st.markdown('<div class="feat-grid"><div class="feat-card"><div class="feat-icon">&#x1F9E0;</div><div class="feat-title">Natural Language Prompt Parsing</div><div class="feat-desc">Write your goal in plain English. The AI detects the task type (classification, regression, clustering) and the target column automatically.</div><span class="feat-badge">Powered by Groq LLaMA 3.3</span></div><div class="feat-card"><div class="feat-icon">&#x26A1;</div><div class="feat-title">AutoML — 15+ Algorithms</div><div class="feat-desc">PyCaret compares Logistic Regression, Random Forest, XGBoost, LightGBM, and 11+ more in one run. Best performer selected automatically.</div><span class="feat-badge">Powered by PyCaret</span></div><div class="feat-card"><div class="feat-icon">&#x1F4CA;</div><div class="feat-title">Interactive Charts</div><div class="feat-desc">Confusion matrix, feature importance, actual vs predicted, residuals — all interactive Plotly charts with hover details.</div><span class="feat-badge">No-Code + Developer</span></div><div class="feat-card"><div class="feat-icon">&#x1F4C4;</div><div class="feat-title">Professional PDF Report</div><div class="feat-desc">7-section report: business context, model justification, metrics, visualizations, feature importance, statistical moments, conclusions.</div><span class="feat-badge">Download-ready</span></div><div class="feat-card"><div class="feat-icon">&#x1F4E6;</div><div class="feat-title">Python Package Export</div><div class="feat-desc">Download a ZIP with model.pkl, predict.py, requirements.txt, and README. Drop into any Python project and start predicting.</div><span class="feat-badge">Developer Mode</span></div><div class="feat-card"><div class="feat-icon">&#x1F310;</div><div class="feat-title">Web App Generator</div><div class="feat-desc">Auto-generates a Streamlit web app with input form for your model features and a live prediction endpoint — ready to deploy.</div><span class="feat-badge">One-click deploy</span></div><div class="feat-card"><div class="feat-icon">&#x1F916;</div><div class="feat-title">AI Assistant</div><div class="feat-desc">Session-aware AI in the sidebar. Knows your model, metrics, and dataset. Ask anything — explanations, tips, Python help.</div><span class="feat-badge">Always available</span></div><div class="feat-card"><div class="feat-icon">&#x270F;</div><div class="feat-title">Prompt Refiner</div><div class="feat-desc">Paste a rough prompt and get 2-3 optimised versions for better task detection — especially useful for ambiguous datasets.</div><span class="feat-badge">In sidebar</span></div><div class="feat-card"><div class="feat-icon">&#x1F4CB;</div><div class="feat-title">Model Comparison Table</div><div class="feat-desc">View scores for every algorithm tested side by side. Understand exactly why AutoML selected the winning model.</div><span class="feat-badge">Developer Mode</span></div></div>', unsafe_allow_html=True)

    # Section 2 — Deployment Guide
    st.markdown('<div class="feat-section-title">Website Deployment Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="feat-section-line"></div>', unsafe_allow_html=True)

    st.markdown('<div class="deploy-header"><div class="deploy-header-icon">&#x1F680;</div><div><div class="deploy-header-title">Deploy Your Model as a Live Web App</div><div class="deploy-header-sub">Train your model &#x2192; Build Website &#x2192; Download ZIP &#x2192; Deploy in 5 minutes. Free hosting available.</div></div></div>', unsafe_allow_html=True)

    # What's inside ZIP
    st.markdown("""<p style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;color:#8899ee;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">What's Inside the Website ZIP</p><div style="background:#13132a;border:1px solid rgba(102,126,234,0.15);border-radius:12px;padding:20px 24px;margin-bottom:24px;"><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;"><div style="display:flex;gap:10px;"><span style="color:#a78bfa;font-size:1.1rem;">&#x1F4C4;</span><div><div style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;color:#ddd;">app_model.py</div><div style="font-size:0.78rem;color:#666;margin-top:2px;">Streamlit web app with auto-generated input form for your features</div></div></div><div style="display:flex;gap:10px;"><span style="color:#a78bfa;font-size:1.1rem;">&#x1F9E0;</span><div><div style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;color:#ddd;">model.pkl</div><div style="font-size:0.78rem;color:#666;margin-top:2px;">Your trained model — serialized and ready to load</div></div></div><div style="display:flex;gap:10px;"><span style="color:#a78bfa;font-size:1.1rem;">&#x1F4CB;</span><div><div style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;color:#ddd;">requirements.txt</div><div style="font-size:0.78rem;color:#666;margin-top:2px;">All Python dependencies pre-listed for deployment</div></div></div><div style="display:flex;gap:10px;"><span style="color:#a78bfa;font-size:1.1rem;">&#x1F4D6;</span><div><div style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;color:#ddd;">README.md</div><div style="font-size:0.78rem;color:#666;margin-top:2px;">Setup and run instructions for local and cloud deployment</div></div></div></div></div>""", unsafe_allow_html=True)

    # Deploy steps
    st.markdown("""<p style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;color:#8899ee;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">Step-by-Step: Deploy on Render (Free)</p><div class="deploy-steps"><div class="deploy-step"><div class="deploy-num">1</div><div><div class="deploy-step-title">Train your model and build the website</div><div class="deploy-step-desc">Complete training in PromptML Studio, then click <strong style="color:#38ef7d;">&#x1F680; Build Website</strong>. Download the ZIP file to your computer.</div></div></div><div class="deploy-step"><div class="deploy-num">2</div><div><div class="deploy-step-title">Extract and push to GitHub</div><div class="deploy-step-desc">Unzip the folder. Create a new GitHub repository and push all files.</div><div style="margin-top:8px;"><span class="code-pill">git init</span> <span class="code-pill">git add .</span> <span class="code-pill">git commit -m "deploy model"</span> <span class="code-pill">git push origin main</span></div><span class="deploy-tip">&#x1F4A1; GitHub account is free — create one at github.com</span></div></div><div class="deploy-step"><div class="deploy-num">3</div><div><div class="deploy-step-title">Create a new Web Service on Render</div><div class="deploy-step-desc">Go to <strong style="color:#38ef7d;">render.com</strong> &#x2192; New &#x2192; Web Service &#x2192; Connect your GitHub repo. Render will auto-detect Python.</div><span class="deploy-tip">&#x1F4A1; Render free tier is enough for demo and portfolio projects</span></div></div><div class="deploy-step"><div class="deploy-num">4</div><div><div class="deploy-step-title">Set the start command</div><div class="deploy-step-desc">In Render settings, set the Start Command to:</div><div style="margin-top:8px;"><span class="code-pill">streamlit run app_model.py --server.port=10000 --server.address=0.0.0.0</span></div></div></div><div class="deploy-step"><div class="deploy-num">5</div><div><div class="deploy-step-title">Deploy and share your live URL</div><div class="deploy-step-desc">Click <strong style="color:#38ef7d;">Create Web Service</strong>. In 2-5 minutes you get a live URL like <span class="code-pill">https://your-model.onrender.com</span></div><span class="deploy-tip">&#x2705; Share this URL with anyone — no login required</span></div></div></div>""", unsafe_allow_html=True)

    # Alternative platforms
    st.markdown('<p style="font-family:\'Outfit\',sans-serif;font-size:0.85rem;font-weight:600;color:#8899ee;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">Alternative Deployment Platforms</p><div class="platform-grid"><div class="platform-card"><div class="platform-icon">&#x1F3E0;</div><div class="platform-name">Streamlit Cloud</div><div class="platform-desc">Easiest option. Connect GitHub repo, done. Best for Streamlit apps.</div><span class="platform-free">Free tier available</span></div><div class="platform-card"><div class="platform-icon">&#x1F5A5;</div><div class="platform-name">Render</div><div class="platform-desc">Reliable, supports any Python web app. Our recommended platform.</div><span class="platform-free">Free tier available</span></div><div class="platform-card"><div class="platform-icon">&#x1F40D;</div><div class="platform-name">Railway / Fly.io</div><div class="platform-desc">Fast deploys, good free tiers. Good for slightly more complex setups.</div><span class="platform-free">Free tier available</span></div></div>', unsafe_allow_html=True)

    # Important notes
    st.markdown('<p style="font-family:\'Outfit\',sans-serif;font-size:0.85rem;font-weight:600;color:#8899ee;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">Important Notes Before Deploying</p>', unsafe_allow_html=True)
    st.markdown('<div class="tip-box"><strong>Render does NOT open new browser tabs.</strong> All navigation in your deployed app must use <code style="color:#a78bfa;">target="_self"</code> on links — never <code style="color:#a78bfa;">target="_blank"</code>.</div>', unsafe_allow_html=True)
    st.markdown('<div class="tip-box"><strong>Free tier spins down after inactivity.</strong> On Render\'s free plan, the app sleeps after 15 minutes of no traffic. First load after sleep takes ~30 seconds. Upgrade to paid for always-on hosting.</div>', unsafe_allow_html=True)
    st.markdown('<div class="tip-box"><strong>PyCaret can be large.</strong> If deployment times out during install, replace <code style="color:#a78bfa;">pycaret</code> in requirements.txt with <code style="color:#a78bfa;">pycaret-lite</code> for a smaller install.</div>', unsafe_allow_html=True)
    st.markdown('<div class="tip-box"><strong>model.pkl must match the Python version.</strong> Ensure your deployment platform uses <strong>Python 3.10+</strong> to avoid compatibility issues with the saved model.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Back button bottom
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="feat_back_bottom"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)