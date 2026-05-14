"""
PromptML Studio — Authentication Page
Login / Sign Up via Supabase Auth
"""
import streamlit as st
import os


def get_supabase():
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def login_ui():
    """Full-screen login / signup page. Sets st.session_state.user on success."""

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Hide streamlit chrome */
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Full page background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 40%, #0a1628 100%) !important;
        min-height: 100vh;
    }

    /* Auth wrapper */
    .auth-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 2rem;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Animated background dots */
    .auth-bg {
        position: fixed;
        inset: 0;
        overflow: hidden;
        z-index: 0;
        pointer-events: none;
    }
    .auth-bg::before {
        content: '';
        position: absolute;
        width: 600px; height: 600px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(102,126,234,0.12) 0%, transparent 70%);
        top: -100px; left: -100px;
        animation: pulse1 8s ease-in-out infinite;
    }
    .auth-bg::after {
        content: '';
        position: absolute;
        width: 500px; height: 500px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(118,75,162,0.10) 0%, transparent 70%);
        bottom: -80px; right: -80px;
        animation: pulse2 10s ease-in-out infinite;
    }
    @keyframes pulse1 {
        0%, 100% { transform: scale(1) translate(0,0); }
        50% { transform: scale(1.15) translate(30px, 20px); }
    }
    @keyframes pulse2 {
        0%, 100% { transform: scale(1) translate(0,0); }
        50% { transform: scale(1.2) translate(-20px, -30px); }
    }

    /* Card */
    .auth-card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 3rem 2.5rem;
        width: 100%;
        max-width: 460px;
        position: relative;
        z-index: 1;
        box-shadow: 0 32px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(102,126,234,0.1);
        animation: cardIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }
    @keyframes cardIn {
        from { opacity: 0; transform: translateY(24px) scale(0.97); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* Logo area */
    .auth-logo {
        text-align: center;
        margin-bottom: 2.2rem;
    }
    .auth-logo-icon {
        font-size: 2.8rem;
        display: block;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 20px rgba(102,126,234,0.6));
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }
    .auth-logo-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
    }
    .auth-logo-sub {
        font-size: 0.82rem;
        color: rgba(255,255,255,0.4);
        margin-top: 0.3rem;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }

    /* Tab pills */
    .auth-tabs {
        display: flex;
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 4px;
        margin-bottom: 1.8rem;
        gap: 4px;
    }
    .auth-tab {
        flex: 1;
        text-align: center;
        padding: 8px 0;
        border-radius: 9px;
        font-size: 0.88rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        color: rgba(255,255,255,0.45);
        font-family: 'Space Grotesk', sans-serif;
    }
    .auth-tab.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 15px rgba(102,126,234,0.35);
    }

    /* Input label override */
    .stTextInput label, .stTextInput > div > div > label {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.55) !important;
        letter-spacing: 0.3px !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }
    .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: rgba(255,255,255,0.9) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 0.9rem !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput input:focus {
        border-color: rgba(102,126,234,0.6) !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.12) !important;
        outline: none !important;
    }

    /* Buttons */
    /* Tab pill buttons — subtle, inactive state */
    button[data-testid="baseButton-secondary"] {
        background: rgba(255,255,255,0.05) !important;
        color: rgba(255,255,255,0.45) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        padding: 0.55rem 0 !important;
        width: 100% !important;
        transition: all 0.2s !important;
        box-shadow: none !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        background: rgba(102,126,234,0.12) !important;
        color: rgba(255,255,255,0.75) !important;
        border-color: rgba(102,126,234,0.3) !important;
    }
    /* Action buttons — Sign In →  /  Create Account → */
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.7rem 1.5rem !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 20px rgba(102,126,234,0.35) !important;
    }
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(102,126,234,0.5) !important;
    }
    button[data-testid="baseButton-primary"]:active {
        transform: translateY(0) !important;
    }

    /* Divider */
    .auth-divider {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 1.4rem 0;
        color: rgba(255,255,255,0.2);
        font-size: 0.78rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .auth-divider::before, .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.08);
    }

    /* Alert boxes */
    .stAlert {
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Footer note */
    .auth-footer-note {
        text-align: center;
        font-size: 0.75rem;
        color: rgba(255,255,255,0.25);
        margin-top: 1.5rem;
        font-family: 'Space Grotesk', sans-serif;
        line-height: 1.6;
    }
    .auth-footer-note a {
        color: rgba(102,126,234,0.7);
        text-decoration: none;
    }

    /* ── Tab-key field navigation ── */
    </style>
    <script>
    (function() {
        function enableTabNav() {
            var inputs = Array.from(document.querySelectorAll(
                '.stTextInput input, .stButton button[kind="primary"], .stButton button'
            )).filter(el => el.offsetParent !== null);
            inputs.forEach(function(el, i) {
                el.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === 'Tab') {
                        e.preventDefault();
                        var next = inputs[i + 1];
                        if (next) { next.focus(); }
                    }
                });
            });
        }
        // Run after Streamlit renders
        setTimeout(enableTabNav, 800);
        setTimeout(enableTabNav, 1500);
    })();
    </script>
    <div class="auth-bg"></div>
    """, unsafe_allow_html=True)

    # ── Centre the card ──────────────────────────────
    _, card_col, _ = st.columns([1, 2, 1])

    with card_col:
        # Logo
        st.markdown("""
        <div class="auth-logo">
            <span class="auth-logo-icon">🤖</span>
            <div class="auth-logo-title">PromptML Studio</div>
            <div class="auth-logo-sub">CSV + Prompt = ML Model</div>
        </div>
        """, unsafe_allow_html=True)

        # Tab selector
        if "auth_tab" not in st.session_state:
            st.session_state.auth_tab = "login"

        tab_login_style  = "active" if st.session_state.auth_tab == "login"  else ""
        tab_signup_style = "active" if st.session_state.auth_tab == "signup" else ""

        # ── Tab switcher — styled pill buttons, no hidden duplicates ──
        st.markdown("""
        <style>
        /* Tab pill buttons */
        div[data-testid="stHorizontalBlock"]:first-of-type button {
            border-radius: 10px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 0.92rem !important;
            font-weight: 500 !important;
            padding: 0.55rem 0 !important;
            border: none !important;
            width: 100% !important;
            transition: all 0.2s !important;
        }
        </style>
        """, unsafe_allow_html=True)

        pill1, pill2 = st.columns(2)
        with pill1:
            is_login = st.session_state.auth_tab == "login"
            if is_login:
                st.markdown("""<div style="background:linear-gradient(135deg,#667eea,#764ba2);
                    color:white;text-align:center;padding:10px 0;border-radius:10px;
                    font-size:0.92rem;font-weight:600;font-family:'Space Grotesk',sans-serif;
                    box-shadow:0 4px 15px rgba(102,126,234,0.4);letter-spacing:0.3px;">
                    🔑 Sign In</div>""", unsafe_allow_html=True)
            else:
                if st.button("🔑 Sign In", key="tab_login_btn", use_container_width=True):
                    st.session_state.auth_tab = "login"
                    st.rerun()
        with pill2:
            is_signup = st.session_state.auth_tab == "signup"
            if is_signup:
                st.markdown("""<div style="background:linear-gradient(135deg,#667eea,#764ba2);
                    color:white;text-align:center;padding:10px 0;border-radius:10px;
                    font-size:0.92rem;font-weight:600;font-family:'Space Grotesk',sans-serif;
                    box-shadow:0 4px 15px rgba(102,126,234,0.4);letter-spacing:0.3px;">
                    ✨ Create Account</div>""", unsafe_allow_html=True)
            else:
                if st.button("✨ Create Account", key="tab_signup_btn", use_container_width=True):
                    st.session_state.auth_tab = "signup"
                    st.rerun()

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

        # ── LOGIN FORM ────────────────────────────────
        if st.session_state.auth_tab == "login":
            email    = st.text_input("Email Address", placeholder="you@example.com",    key="login_email")
            password = st.text_input("Password",      placeholder="••••••••",           key="login_password", type="password")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            if st.button("Sign In →", key="login_btn", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in both fields.")
                else:
                    sb = get_supabase()
                    if not sb:
                        st.error("⚠️ Supabase not configured. Check your secrets.")
                    else:
                        try:
                            resp = sb.auth.sign_in_with_password({"email": email, "password": password})
                            st.session_state.user = resp.user
                            st.session_state.access_token = resp.session.access_token
                            st.success(f"✅ Welcome back, {resp.user.email}!")
                            st.rerun()
                        except Exception as e:
                            err = str(e)
                            if "Invalid login" in err or "invalid_grant" in err:
                                st.error("❌ Incorrect email or password.")
                            elif "Email not confirmed" in err:
                                st.warning("📧 Please verify your email first. Check your inbox.")
                            else:
                                st.error(f"❌ Login failed: {err}")

            st.markdown("""
            <div class="auth-footer-note">
                Don't have an account? Click <b>Sign Up</b> above.<br>
                Forgot password? Contact your admin or re-register.
            </div>
            """, unsafe_allow_html=True)

        # ── SIGN UP FORM ──────────────────────────────
        else:
            name     = st.text_input("Full Name",        placeholder="Yaswant Khedkar",  key="signup_name")
            email    = st.text_input("Email Address",    placeholder="you@example.com",   key="signup_email")
            password = st.text_input("Password",         placeholder="min 6 characters",  key="signup_password",  type="password")
            confirm  = st.text_input("Confirm Password", placeholder="••••••••",          key="signup_confirm",   type="password")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            if st.button("Create Account →", key="signup_btn", use_container_width=True, type="primary"):
                if not name or not email or not password or not confirm:
                    st.error("Please fill in all fields.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    sb = get_supabase()
                    if not sb:
                        st.error("⚠️ Supabase not configured. Check your secrets.")
                    else:
                        try:
                            resp = sb.auth.sign_up({
                                "email": email,
                                "password": password,
                                "options": {"data": {"full_name": name}}
                            })
                            if resp.user:
                                # Check if email confirmation required
                                if resp.user.confirmed_at is None and resp.session is None:
                                    st.success("📧 Account created! Please check your email to verify your account, then sign in.")
                                    st.session_state.auth_tab = "login"
                                else:
                                    # Auto-login if no email confirmation required
                                    st.session_state.user = resp.user
                                    st.session_state.access_token = resp.session.access_token if resp.session else ""
                                    st.success(f"🎉 Welcome to PromptML Studio, {name}!")
                                    st.rerun()
                        except Exception as e:
                            err = str(e)
                            if "already registered" in err or "already exists" in err:
                                st.error("❌ This email is already registered. Please sign in instead.")
                            elif "invalid" in err.lower() and "email" in err.lower():
                                st.error("❌ Invalid email address.")
                            else:
                                st.error(f"❌ Sign up failed: {err}")

            st.markdown("""
            <div class="auth-footer-note">
                Already have an account? Click <b>Sign In</b> above.<br>
                By signing up you agree to use this platform responsibly.
            </div>
            """, unsafe_allow_html=True)