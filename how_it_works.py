"""
PromptML Studio - How It Works Page
"""
import streamlit as st


def show_how_it_works_page():
    """Render the How It Works page"""

    def go_home():
        st.session_state.current_page = "home"
        st.session_state.mode = None
        st.query_params.clear()
        st.rerun()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

    /* ── Shared with About ── */
    .hiw-hero {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px;
        padding: 56px 48px;
        text-align: center;
        margin-bottom: 36px;
        position: relative;
        overflow: hidden;
    }
    .hiw-hero-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #8899ee;
        margin-bottom: 14px;
    }
    .hiw-hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 30%, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 18px;
        line-height: 1.15;
    }
    .hiw-hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: rgba(255,255,255,0.6);
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.7;
    }
    .hiw-section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
        margin-top: 8px;
    }
    .hiw-section-line {
        width: 44px;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
        margin-bottom: 24px;
    }

    /* ── Role selector cards ── */
    .role-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 36px;
    }
    .role-card {
        background: #13132a;
        border: 1px solid rgba(102,126,234,0.15);
        border-radius: 14px;
        padding: 28px 24px;
        position: relative;
        overflow: hidden;
    }
    .role-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 14px 14px 0 0;
    }
    .role-card.nocode::before { background: linear-gradient(90deg, #667eea, #764ba2); }
    .role-card.developer::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
    .role-icon { font-size: 2rem; margin-bottom: 10px; }
    .role-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 8px;
    }
    .role-who {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: #8899ee;
        font-weight: 500;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .role-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #888;
        line-height: 1.6;
    }
    .role-tag {
        display: inline-block;
        margin-top: 12px;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    .role-card.nocode .role-tag {
        background: rgba(102,126,234,0.12);
        border: 1px solid rgba(102,126,234,0.25);
        color: #8899ee;
    }
    .role-card.developer .role-tag {
        background: rgba(17,153,142,0.12);
        border: 1px solid rgba(17,153,142,0.3);
        color: #38ef7d;
    }

    /* ── Mode section header ── */
    .mode-header {
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .mode-header.nocode {
        background: linear-gradient(135deg, rgba(102,126,234,0.12), rgba(118,75,162,0.08));
        border: 1px solid rgba(102,126,234,0.2);
    }
    .mode-header.developer {
        background: linear-gradient(135deg, rgba(17,153,142,0.1), rgba(56,239,125,0.06));
        border: 1px solid rgba(17,153,142,0.2);
    }
    .mode-header-icon { font-size: 1.8rem; }
    .mode-header-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
    }
    .mode-header-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: #888;
        margin-top: 2px;
    }

    /* ── Step cards ── */
    .steps-wrapper {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-bottom: 28px;
    }
    .step-card {
        background: #16162a;
        border: 1px solid rgba(102,126,234,0.12);
        border-radius: 12px;
        padding: 18px 20px;
        display: flex;
        gap: 16px;
        align-items: flex-start;
    }
    .step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        color: #fff;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .step-number.green {
        background: linear-gradient(135deg, #11998e, #38ef7d);
    }
    .step-content {}
    .step-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        color: #ddd;
        margin-bottom: 4px;
    }
    .step-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #777;
        line-height: 1.6;
    }
    .step-tip {
        display: inline-block;
        margin-top: 6px;
        font-family: 'Inter', sans-serif;
        font-size: 0.76rem;
        color: #667eea;
        background: rgba(102,126,234,0.08);
        border-radius: 6px;
        padding: 3px 10px;
    }
    .step-tip.green { color: #38ef7d; background: rgba(56,239,125,0.08); }

    /* ── Button reference cards ── */
    .btn-ref-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 28px;
    }
    .btn-ref-card {
        background: #13132a;
        border: 1px solid rgba(102,126,234,0.1);
        border-radius: 10px;
        padding: 14px 16px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }
    .btn-ref-icon {
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    .btn-ref-name {
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: #c5caff;
        margin-bottom: 3px;
    }
    .btn-ref-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: #666;
        line-height: 1.5;
    }

    /* ── Flow diagram ── */
    .flow-diagram {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin: 20px 0 32px 0;
        flex-wrap: wrap;
    }
    .flow-box {
        background: #13132a;
        border: 1px solid rgba(102,126,234,0.2);
        border-radius: 10px;
        padding: 12px 18px;
        text-align: center;
        min-width: 100px;
    }
    .flow-box-icon { font-size: 1.4rem; margin-bottom: 4px; }
    .flow-box-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: #aaa;
        font-weight: 500;
    }
    .flow-arrow {
        font-size: 1.2rem;
        color: #667eea;
        padding: 0 8px;
        font-weight: bold;
    }

    /* ── Assistant features ── */
    .assistant-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 28px;
    }
    .assistant-card {
        background: #13132a;
        border: 1px solid rgba(102,126,234,0.12);
        border-radius: 12px;
        padding: 20px 18px;
        position: relative;
    }
    .assistant-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 12px 12px 0 0;
        opacity: 0.6;
    }
    .assistant-icon { font-size: 1.4rem; margin-bottom: 8px; }
    .assistant-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: #ddd;
        margin-bottom: 6px;
    }
    .assistant-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.79rem;
        color: #666;
        line-height: 1.6;
    }

    /* ── Pro tips ── */
    .tip-box {
        background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.05));
        border: 1px solid rgba(102,126,234,0.2);
        border-left: 3px solid #667eea;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 0.84rem;
        color: #b0b0c8;
        line-height: 1.7;
    }
    .tip-box strong { color: #c5caff; }

    /* ── Back button ── */
    div[data-testid="stButton"].back-btn > button {
        background: rgba(102,126,234,0.1) !important;
        border: 1px solid rgba(102,126,234,0.3) !important;
        color: #8899ee !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px !important;
        padding: 6px 16px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stButton"].back-btn > button:hover {
        background: rgba(102,126,234,0.2) !important;
        color: #c5caff !important;
        transform: none !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Top Back Button ──────────────────────────────────────
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="hiw_back_top"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────
    st.markdown("""
    <div class="hiw-hero">
        <div class="hiw-hero-label">Documentation</div>
        <div class="hiw-hero-title">How It Works</div>
        <div class="hiw-hero-sub">
            A complete guide to using PromptML Studio —
            from uploading your data to getting a production-ready ML model in minutes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION 1 — IDENTIFY YOUR ROLE
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="hiw-section-title">1. Identify Your Role</div>', unsafe_allow_html=True)
    st.markdown('<div class="hiw-section-line"></div>', unsafe_allow_html=True)

    st.markdown("""
    <p style="font-family:'Inter',sans-serif;font-size:0.9rem;color:#888;margin-bottom:20px;line-height:1.7;">
        PromptML Studio has two modes. Choose based on what you need — you can switch anytime.
    </p>
    <div class="role-grid">
        <div class="role-card nocode">
            <div class="role-icon">📱</div>
            <div class="role-title">No-Code Mode</div>
            <div class="role-who">For Business Users &amp; Analysts</div>
            <div class="role-desc">
                You have data and a business question. You want answers, charts,
                and reports — without writing a single line of code.
            </div>
            <span class="role-tag">Recommended for beginners</span>
        </div>
        <div class="role-card developer">
            <div class="role-icon">💻</div>
            <div class="role-title">Developer Mode</div>
            <div class="role-who">For Developers &amp; ML Engineers</div>
            <div class="role-desc">
                You want the trained model file, prediction scripts, requirements,
                and a deployable Python package — ready for production.
            </div>
            <span class="role-tag">For technical users</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Visual flow diagram ──────────────────────────────────
    st.markdown("""
    <div class="flow-diagram">
        <div class="flow-box">
            <div class="flow-box-icon">📂</div>
            <div class="flow-box-label">Upload CSV</div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-box">
            <div class="flow-box-icon">💬</div>
            <div class="flow-box-label">Write Prompt</div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-box">
            <div class="flow-box-icon">🤖</div>
            <div class="flow-box-label">AutoML Trains</div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-box">
            <div class="flow-box-icon">📊</div>
            <div class="flow-box-label">Results</div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-box">
            <div class="flow-box-icon">🚀</div>
            <div class="flow-box-label">Deploy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION 2 — NO-CODE MODE
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="hiw-section-title">2. No-Code Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="hiw-section-line"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="mode-header nocode">
        <div class="mode-header-icon">📱</div>
        <div>
            <div class="mode-header-title">No-Code Mode — Step by Step</div>
            <div class="mode-header-sub">Upload → Prompt → Train → Download Report. No coding needed.</div>
        </div>
    </div>

    <div class="steps-wrapper">
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-content">
                <div class="step-title">Select No-Code Mode</div>
                <div class="step-desc">On the home screen, click the <strong style="color:#c5caff;">📱 No-Code Mode</strong> button.
                You'll land on the data upload screen.</div>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-content">
                <div class="step-title">Upload Your CSV Dataset</div>
                <div class="step-desc">Drag and drop your CSV file or click to browse.
                Your file should have column headers in the first row.
                Minimum recommended: 30+ rows for meaningful results.</div>
                <span class="step-tip">💡 No CSV? Use the sample datasets — House Prices or Customer Churn.</span>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-content">
                <div class="step-title">Write Your Prompt</div>
                <div class="step-desc">In plain English, describe what you want to predict.
                The AI reads your prompt and automatically detects the task type and target column.</div>
                <span class="step-tip">💡 Good prompt: "Predict customer churn based on usage data"</span>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number">4</div>
            <div class="step-content">
                <div class="step-title">Click Build ML Model</div>
                <div class="step-desc">The AutoML engine compares 15+ algorithms, picks the best one,
                trains it on your data, and evaluates performance — all automatically. Takes 30–90 seconds.</div>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number">5</div>
            <div class="step-content">
                <div class="step-title">Read Your Results</div>
                <div class="step-desc">View performance metrics (Accuracy, F1, R², RMSE), interactive charts,
                and feature importance. Every number has an inference explaining what it means for your business.</div>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number">6</div>
            <div class="step-content">
                <div class="step-title">Download Your Outputs</div>
                <div class="step-desc">Export a <strong style="color:#c5caff;">Predictions CSV</strong> with model outputs
                on every row, or generate a full <strong style="color:#c5caff;">PDF Report</strong> with charts,
                business context, and model explanation.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Button reference — No-Code
    st.markdown("""
    <p style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;
        color:#8899ee;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">
        Button Reference — No-Code Mode
    </p>
    <div class="btn-ref-grid">
        <div class="btn-ref-card">
            <div class="btn-ref-icon">📝</div>
            <div>
                <div class="btn-ref-name">Use Sample Dataset</div>
                <div class="btn-ref-desc">Load a pre-built CSV so you can try the platform without having your own data ready.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">🚀</div>
            <div>
                <div class="btn-ref-name">Build ML Model</div>
                <div class="btn-ref-desc">Starts AutoML — parses prompt, selects algorithm, trains model, evaluates results.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">📊</div>
            <div>
                <div class="btn-ref-name">Download Predictions CSV</div>
                <div class="btn-ref-desc">Exports a CSV file with the model's prediction for every row in your dataset.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">📄</div>
            <div>
                <div class="btn-ref-name">Generate PDF Report</div>
                <div class="btn-ref-desc">Creates a professional 7-section PDF report with charts, metrics, business context, and limitations.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">🌍</div>
            <div>
                <div class="btn-ref-name">Build Website</div>
                <div class="btn-ref-desc">Generates a deployable Streamlit web app for your model — ready to host on Render or Streamlit Cloud.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">👁️</div>
            <div>
                <div class="btn-ref-name">Preview Website</div>
                <div class="btn-ref-desc">Shows a live preview of the generated web app directly inside the platform.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION 3 — DEVELOPER MODE
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="hiw-section-title">3. Developer Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="hiw-section-line"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="mode-header developer">
        <div class="mode-header-icon">💻</div>
        <div>
            <div class="mode-header-title">Developer Mode — Step by Step</div>
            <div class="mode-header-sub">Same workflow as No-Code, but outputs a production-ready Python package.</div>
        </div>
    </div>

    <div class="steps-wrapper">
        <div class="step-card">
            <div class="step-number green">1</div>
            <div class="step-content">
                <div class="step-title">Select Developer Mode</div>
                <div class="step-desc">On the home screen, click <strong style="color:#38ef7d;">💻 Developer Mode</strong>.
                Everything works the same as No-Code — but the outputs are different.</div>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number green">2</div>
            <div class="step-content">
                <div class="step-title">Upload CSV + Write Prompt</div>
                <div class="step-desc">Same as No-Code Mode. Upload your dataset and describe the task in plain English.
                The AI handles task detection automatically.</div>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number green">3</div>
            <div class="step-content">
                <div class="step-title">Train the Model</div>
                <div class="step-desc">Click <strong style="color:#38ef7d;">Build ML Model</strong>. AutoML runs the same pipeline —
                you additionally get a model comparison table showing all algorithms evaluated.</div>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number green">4</div>
            <div class="step-content">
                <div class="step-title">Generate Python Package</div>
                <div class="step-desc">Click <strong style="color:#38ef7d;">Generate Python Package</strong> to download a ZIP
                containing: <code style="color:#a78bfa;background:rgba(167,139,250,0.1);padding:1px 6px;border-radius:4px;">model.pkl</code>,
                <code style="color:#a78bfa;background:rgba(167,139,250,0.1);padding:1px 6px;border-radius:4px;">predict.py</code>,
                <code style="color:#a78bfa;background:rgba(167,139,250,0.1);padding:1px 6px;border-radius:4px;">requirements.txt</code>,
                and <code style="color:#a78bfa;background:rgba(167,139,250,0.1);padding:1px 6px;border-radius:4px;">README.md</code>.</div>
                <span class="step-tip green">💡 Run: pip install -r requirements.txt → python predict.py your_data.csv</span>
            </div>
        </div>
        <div class="step-card">
            <div class="step-number green">5</div>
            <div class="step-content">
                <div class="step-title">Deploy as a Web App</div>
                <div class="step-desc">Click <strong style="color:#38ef7d;">Build Website</strong> to generate a complete
                Streamlit web app with an input form and prediction endpoint.
                Download the ZIP and deploy to any cloud platform.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Button reference — Developer
    st.markdown("""
    <p style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;
        color:#38ef7d;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;opacity:0.8;">
        Button Reference — Developer Mode
    </p>
    <div class="btn-ref-grid">
        <div class="btn-ref-card">
            <div class="btn-ref-icon">📊</div>
            <div>
                <div class="btn-ref-name">Download Predictions CSV</div>
                <div class="btn-ref-desc">Same as No-Code — exports predictions for every row as a CSV file.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">📄</div>
            <div>
                <div class="btn-ref-name">Generate PDF Report</div>
                <div class="btn-ref-desc">Full 7-section technical report — same as No-Code, ideal for documentation.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">🔨</div>
            <div>
                <div class="btn-ref-name">Generate Python Package</div>
                <div class="btn-ref-desc">Downloads a ZIP with model.pkl, predict.py, requirements.txt, and README. Plug into any Python project.</div>
            </div>
        </div>
        <div class="btn-ref-card">
            <div class="btn-ref-icon">📋</div>
            <div>
                <div class="btn-ref-name">View All Models Comparison</div>
                <div class="btn-ref-desc">Expandable table showing every algorithm tested with its scores — helps you understand why AutoML chose the winner.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION 4 — PROMPTML ASSISTANT
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="hiw-section-title">4. PromptML Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="hiw-section-line"></div>', unsafe_allow_html=True)

    st.markdown("""
    <p style="font-family:'Inter',sans-serif;font-size:0.9rem;color:#888;margin-bottom:20px;line-height:1.7;">
        The AI assistant lives in the left sidebar. It knows your current session — your model, metrics, and dataset —
        and can answer any ML or platform question instantly.
    </p>

    <div class="assistant-grid">
        <div class="assistant-card">
            <div class="assistant-icon">✨</div>
            <div class="assistant-title">Prompt Refiner</div>
            <div class="assistant-desc">Paste a rough prompt and get 2–3 improved versions optimised for better ML task detection.</div>
        </div>
        <div class="assistant-card">
            <div class="assistant-icon">💡</div>
            <div class="assistant-title">FAQ Quick Questions</div>
            <div class="assistant-desc">One-click answers to common questions — Accuracy, R², RMSE, overfitting, and how to improve your model.</div>
        </div>
        <div class="assistant-card">
            <div class="assistant-icon">🧠</div>
            <div class="assistant-title">Session-Aware Chat</div>
            <div class="assistant-desc">Ask anything about your current results. The assistant knows your model type, target column, and performance metrics.</div>
        </div>
        <div class="assistant-card">
            <div class="assistant-icon">📚</div>
            <div class="assistant-title">ML Education</div>
            <div class="assistant-desc">Ask about any ML concept — Random Forest, cross-validation, feature engineering — explained in plain English.</div>
        </div>
        <div class="assistant-card">
            <div class="assistant-icon">🐍</div>
            <div class="assistant-title">Python Help</div>
            <div class="assistant-desc">Get help with pandas, scikit-learn, NumPy, or any Python data science question while working on your project.</div>
        </div>
        <div class="assistant-card">
            <div class="assistant-icon">🗑️</div>
            <div class="assistant-title">Clear Chat</div>
            <div class="assistant-desc">Hit Clear to reset the conversation and start fresh — useful when switching datasets or tasks.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pro tips
    st.markdown("""
    <p style="font-family:'Outfit',sans-serif;font-size:0.85rem;font-weight:600;
        color:#8899ee;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">
        Pro Tips for the Assistant
    </p>

    <div class="tip-box">
        <strong>Use the Prompt Refiner first.</strong> Before building your model, paste your prompt into the
        Prompt Refiner. A better prompt = better task detection = better model results.
    </div>
    <div class="tip-box">
        <strong>Ask "why" questions.</strong> After training, ask the assistant: <em>"Why is my accuracy low?"</em>
        or <em>"What does this F1 score mean for my business?"</em> — it uses your actual results to answer.
    </div>
    <div class="tip-box">
        <strong>Use the FAQ dropdown for quick learning.</strong> If you're unsure what a metric means,
        select it from the FAQ dropdown and click Ask — you'll get a simple, real-life explanation instantly.
    </div>
    <div class="tip-box">
        <strong>Ask for improvement tips.</strong> Try: <em>"How can I improve my model's R² score?"</em>
        or <em>"My dataset has 50 rows — is that enough?"</em> The assistant gives actionable, specific advice.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bottom Back Button ────────────────────────────────────
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="hiw_back_bottom"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)