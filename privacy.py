"""
PromptML Studio - Privacy Policy Page
"""
import streamlit as st


def show_privacy_page():
    """Render the Privacy Policy page"""

    def go_home():
        st.session_state.current_page = "home"
        st.session_state.mode = None
        st.query_params.clear()
        st.rerun()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
    .priv-hero { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); border-radius: 16px; padding: 48px 48px; text-align: center; margin-bottom: 36px; position: relative; overflow: hidden; }
    .priv-hero-label { font-family: 'Inter', sans-serif; font-size: 0.72rem; font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase; color: #8899ee; margin-bottom: 14px; }
    .priv-hero-title { font-family: 'Outfit', sans-serif; font-size: 2.6rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 30%, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 14px; line-height: 1.15; }
    .priv-hero-sub { font-family: 'Inter', sans-serif; font-size: 0.88rem; color: rgba(255,255,255,0.45); max-width: 480px; margin: 0 auto; line-height: 1.6; }
    .priv-section-title { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 6px; margin-top: 8px; }
    .priv-section-line { width: 44px; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 2px; margin-bottom: 24px; }
    .priv-card { background: #13132a; border: 1px solid rgba(102,126,234,0.12); border-radius: 14px; padding: 26px 28px; margin-bottom: 14px; position: relative; }
    .priv-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 14px 14px 0 0; opacity: 0.5; }
    .priv-card-title { font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: #c5caff; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    .priv-card-icon { font-size: 1.1rem; }
    .priv-card-body { font-family: 'Inter', sans-serif; font-size: 0.83rem; color: #777; line-height: 1.8; }
    .priv-card-body strong { color: #b0b0c8; font-weight: 600; }
    .priv-highlight { background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.05)); border: 1px solid rgba(102,126,234,0.18); border-left: 3px solid #667eea; border-radius: 10px; padding: 16px 20px; margin-bottom: 28px; font-family: 'Inter', sans-serif; font-size: 0.84rem; color: #b0b0c8; line-height: 1.75; }
    .priv-highlight strong { color: #c5caff; }
    .priv-updated { font-family: 'Inter', sans-serif; font-size: 0.75rem; color: #444; text-align: right; margin-bottom: 28px; }
    div[data-testid="stButton"].back-btn > button { background: rgba(102,126,234,0.1) !important; border: 1px solid rgba(102,126,234,0.3) !important; color: #8899ee !important; font-size: 0.85rem !important; font-family: 'Inter', sans-serif !important; border-radius: 8px !important; padding: 6px 16px !important; }
    div[data-testid="stButton"].back-btn > button:hover { background: rgba(102,126,234,0.2) !important; color: #c5caff !important; transform: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Top Back Button
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="priv_back_top"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Hero
    st.markdown('<div class="priv-hero"><div class="priv-hero-label">Legal</div><div class="priv-hero-title">Privacy Policy</div><div class="priv-hero-sub">We respect your privacy. This page explains what data PromptML Studio handles and how we protect it.</div></div>', unsafe_allow_html=True)

    # Last updated
    st.markdown('<div class="priv-updated">Last updated: March 2026</div>', unsafe_allow_html=True)

    # Intro highlight
    st.markdown('<div class="priv-highlight"><strong>Short version:</strong> PromptML Studio does not collect, store, or sell any personal data. Your uploaded datasets and trained models exist only within your browser session and are never transmitted to or stored on our servers.</div>', unsafe_allow_html=True)

    # Section title
    st.markdown('<div class="priv-section-title">Our Privacy Commitments</div>', unsafe_allow_html=True)
    st.markdown('<div class="priv-section-line"></div>', unsafe_allow_html=True)

    # Cards — all single line to avoid Streamlit HTML escaping
    st.markdown('<div class="priv-card"><div class="priv-card-title"><span class="priv-card-icon">&#x1F4C2;</span> Data You Upload</div><div class="priv-card-body">Any CSV file you upload to PromptML Studio is processed <strong>entirely within your current browser session</strong>. We do not store, log, or retain your dataset on any server. Once you close or refresh the tab, the data is gone. We never have access to the content of your files.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="priv-card"><div class="priv-card-title"><span class="priv-card-icon">&#x1F9E0;</span> Trained Models</div><div class="priv-card-body">Models trained using PromptML Studio exist only in your active session memory. Downloaded model files (model.pkl, ZIP packages) are generated on-demand and delivered directly to your browser. <strong>We do not keep copies</strong> of your trained models on our infrastructure.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="priv-card"><div class="priv-card-title"><span class="priv-card-icon">&#x1F916;</span> AI Assistant (Groq API)</div><div class="priv-card-body">The PromptML Assistant uses the <strong>Groq LLaMA 3.3 API</strong> to respond to your questions. Messages sent to the assistant are transmitted to Groq\'s servers for processing. We recommend not sharing sensitive personal or confidential business data through the assistant chat. Groq\'s own privacy policy governs how they handle API requests.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="priv-card"><div class="priv-card-title"><span class="priv-card-icon">&#x1F36A;</span> Cookies &amp; Tracking</div><div class="priv-card-body">PromptML Studio does <strong>not use cookies</strong>, analytics trackers, or any third-party tracking scripts. We do not collect browsing behavior, usage statistics, or any personally identifiable information (PII). Streamlit\'s session state is used only to maintain your current workflow within the active tab.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="priv-card"><div class="priv-card-title"><span class="priv-card-icon">&#x2709;</span> Contact &amp; Email</div><div class="priv-card-body">If you contact us at <strong>promptmlstudio@gmail.com</strong>, we will use your email address solely to respond to your query. We do not add you to any mailing list, share your email with third parties, or use it for any marketing purpose.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="priv-card"><div class="priv-card-title"><span class="priv-card-icon">&#x1F512;</span> Data Security</div><div class="priv-card-body">Since we do not store your data, there is no database of user information that could be breached. The platform runs over HTTPS on Render\'s infrastructure. All data processing happens transiently — nothing is written to disk beyond the active session.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="priv-card"><div class="priv-card-title"><span class="priv-card-icon">&#x1F4DD;</span> Changes to This Policy</div><div class="priv-card-body">If we ever change this Privacy Policy, the updated version will be published on this page with a revised date. Since we are an academic diploma project, significant changes are unlikely — but we are committed to being transparent if they occur.</div></div>', unsafe_allow_html=True)

    # Contact line
    st.markdown('<div class="priv-highlight" style="margin-top:28px;">Questions about this policy? Email us at <strong>promptmlstudio@gmail.com</strong> — we will respond within 1 business day.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bottom Back Button
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="priv_back_bottom"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)