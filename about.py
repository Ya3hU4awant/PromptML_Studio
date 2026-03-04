"""
PromptML Studio - About Page
"""
import streamlit as st


def show_about_page():
    """Render the full About page"""

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

    .about-hero {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px;
        padding: 56px 48px;
        text-align: center;
        margin-bottom: 36px;
        position: relative;
        overflow: hidden;
    }
    .about-hero-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #8899ee;
        margin-bottom: 14px;
    }
    .about-hero-title {
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
    .about-hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: rgba(255,255,255,0.6);
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.7;
    }
    .about-section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
        margin-top: 8px;
    }
    .about-section-line {
        width: 44px;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
        margin-bottom: 24px;
    }
    .about-text-card {
        background: #16162a;
        border: 1px solid rgba(102,126,234,0.15);
        border-radius: 14px;
        padding: 28px 32px;
        margin-bottom: 32px;
        font-family: 'Inter', sans-serif;
        font-size: 0.93rem;
        color: #b0b0c8;
        line-height: 1.85;
    }
    .about-text-card p { margin-bottom: 12px; }
    .about-text-card p:last-child { margin-bottom: 0; }
    .about-text-card strong { color: #c5caff; font-weight: 600; }

    .stats-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 36px;
    }
    .stat-item {
        background: #13132a;
        border: 1px solid rgba(102,126,234,0.12);
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
    }
    .stat-number {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-bottom: 6px;
    }
    .stat-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .belief-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 36px;
    }
    .belief-card {
        background: #13132a;
        border: 1px solid rgba(102,126,234,0.12);
        border-radius: 12px;
        padding: 22px 20px;
        position: relative;
    }
    .belief-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 12px 12px 0 0;
        opacity: 0.7;
    }
    .belief-icon { font-size: 1.5rem; margin-bottom: 10px; }
    .belief-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.92rem;
        font-weight: 600;
        color: #ddd;
        margin-bottom: 7px;
    }
    .belief-text {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: #777;
        line-height: 1.6;
    }

    .team-wrapper {
        display: grid;
        grid-template-columns: 3fr 2fr;
        gap: 24px;
        margin-bottom: 40px;
    }
    .team-panel {
        background: #13132a;
        border: 1px solid rgba(102,126,234,0.12);
        border-radius: 14px;
        padding: 24px;
    }
    .team-panel-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #667eea;
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(102,126,234,0.15);
    }
    .team-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .member-card {
        display: flex;
        align-items: center;
        gap: 11px;
        background: rgba(102,126,234,0.05);
        border: 1px solid rgba(102,126,234,0.1);
        border-radius: 10px;
        padding: 11px 13px;
    }
    .member-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        color: #fff;
        flex-shrink: 0;
    }
    .member-name {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: #ddd;
        line-height: 1.2;
    }
    .member-role {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        color: #666;
        margin-top: 2px;
    }
    .advisor-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 28px 16px;
        gap: 12px;
    }
    .advisor-avatar {
        width: 76px;
        height: 76px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        background: linear-gradient(135deg, #764ba2, #667eea);
        box-shadow: 0 0 0 4px rgba(102,126,234,0.2);
    }
    .advisor-name {
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #fff;
    }
    .advisor-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: #8899ee;
        line-height: 1.5;
    }
    .advisor-badge {
        background: rgba(102,126,234,0.12);
        border: 1px solid rgba(102,126,234,0.25);
        border-radius: 20px;
        padding: 4px 14px;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        color: #8899ee;
        font-weight: 500;
    }
    .advisor-quote {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: #555;
        font-style: italic;
        line-height: 1.6;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding-top: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Back button ──────────────────────────────────────────
    if st.button("← Back to PromptML Studio", key="about_back_top"):
        st.session_state.current_page = "home"
        st.session_state.mode = None
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────
    st.markdown("""
    <div class="about-hero">
        <div class="about-hero-label">About Us</div>
        <div class="about-hero-title">PromptML Studio</div>
        <div class="about-hero-sub">
            An AI-powered AutoML platform built by students, for everyone —
            turning raw data and plain English into production-ready ML models.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats ─────────────────────────────────────────────────
    st.markdown("""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-number">3</div>
            <div class="stat-label">ML Task Types</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">15+</div>
            <div class="stat-label">Algorithms Compared</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">7</div>
            <div class="stat-label">Team Members</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">0</div>
            <div class="stat-label">Code Required</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── About ─────────────────────────────────────────────────
    st.markdown('<div class="about-section-title">About PromptML Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="about-section-line"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="about-text-card">
        <p><strong>PromptML Studio</strong> is an AI-powered AutoML platform that eliminates the barrier
        between raw data and machine learning. Upload a CSV, describe your goal in plain English,
        and receive a fully trained production-ready model — instantly.</p>
        <p>Built on <strong>PyCaret AutoML</strong> and powered by <strong>Groq LLaMA 3.3</strong>,
        the platform parses your intent, selects the right algorithm, trains multiple models,
        and delivers results with professional PDF reports, interactive visualizations,
        and deployable Python packages.</p>
        <p>Two tailored modes — <strong>No-Code Mode</strong> for instant insights and
        <strong>Developer Mode</strong> for production-ready packages — making ML accessible to everyone.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Who We Are ───────────────────────────────────────────
    st.markdown('<div class="about-section-title">Who We Are</div>', unsafe_allow_html=True)
    st.markdown('<div class="about-section-line"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="about-text-card">
        <p>We are a team of <strong>seven diploma students</strong> from
        <strong>Government Polytechnic, Chhatrapati Sambhajinagar</strong>, passionate about
        AI and Machine Learning. This project was born from a shared belief that the power of
        machine learning should not be locked behind years of programming expertise.</p>
        <p>Guided by our advisor <strong>N.M. Masuldar</strong>, Lecturer at Government Polytechnic,
        we designed and built PromptML Studio as our AIML Diploma Project — combining real-world
        software engineering, cloud deployment, and modern AI tooling into one cohesive platform.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── What We Believe ──────────────────────────────────────
    st.markdown('<div class="about-section-title">What We Believe In</div>', unsafe_allow_html=True)
    st.markdown('<div class="about-section-line"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="belief-grid">
        <div class="belief-card">
            <div class="belief-icon">&#x1F513;</div>
            <div class="belief-title">Democratization</div>
            <div class="belief-text">Machine learning should be accessible to every professional,
            not just those with advanced degrees in data science.</div>
        </div>
        <div class="belief-card">
            <div class="belief-icon">&#x26A1;</div>
            <div class="belief-title">Speed Without Compromise</div>
            <div class="belief-text">AutoML removes repetitive work so users can focus on the
            problem that actually matters — not the pipeline.</div>
        </div>
        <div class="belief-card">
            <div class="belief-icon">&#x1F50D;</div>
            <div class="belief-title">Transparency</div>
            <div class="belief-text">Every model decision is explainable. Feature importance,
            business inferences, and honest limitations built into every report.</div>
        </div>
        <div class="belief-card">
            <div class="belief-icon">&#x1F3D7;</div>
            <div class="belief-title">Production Readiness</div>
            <div class="belief-text">A model that cannot be deployed is just an experiment.
            We build tools that go from CSV to live API in minutes.</div>
        </div>
        <div class="belief-card">
            <div class="belief-icon">&#x1F91D;</div>
            <div class="belief-title">Human + AI Collaboration</div>
            <div class="belief-text">AI should augment human decision-making, not replace it.
            Our platform keeps humans in control with clear, actionable outputs.</div>
        </div>
        <div class="belief-card">
            <div class="belief-icon">&#x1F4DA;</div>
            <div class="belief-title">Learning by Doing</div>
            <div class="belief-text">The best way to understand ML is to use it. Every inference
            box in our reports is an educational moment.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Meet the Team ─────────────────────────────────────────
    st.markdown('<div class="about-section-title">Meet the Team</div>', unsafe_allow_html=True)
    st.markdown('<div class="about-section-line"></div>', unsafe_allow_html=True)

    team = [
        ("Yash Udawant",     "YU", "ML Engineer",             "linear-gradient(135deg,#667eea,#764ba2)"),
        ("Shubham Hajare",   "SH", "Backend Developer",       "linear-gradient(135deg,#11998e,#38ef7d)"),
        ("Tamanna Shaikh",   "TS", "Data Scientist",          "linear-gradient(135deg,#e96c6c,#c0392b)"),
        ("Gangotri Borade",  "GB", "UI/UX Designer",          "linear-gradient(135deg,#f7971e,#ffd200)"),
        ("Pratik Pawar",     "PP", "ML Engineer",             "linear-gradient(135deg,#00b4d8,#0077b6)"),
        ("Sanskar Sutawane", "SS", "Full Stack Developer",    "linear-gradient(135deg,#a18cd1,#fbc2eb)"),
        ("Rani Gaikwad",     "RG", "Data Analyst",            "linear-gradient(135deg,#43e97b,#38f9d7)"),
    ]

    team_html = '<div class="team-grid">'
    for name, initials, role, color in team:
        team_html += f"""
        <div class="member-card">
            <div class="member-avatar" style="background:{color};">{initials}</div>
            <div>
                <div class="member-name">{name}</div>
                <div class="member-role">{role}</div>
            </div>
        </div>"""
    team_html += '</div>'

    st.markdown(f"""
    <div class="team-wrapper">
        <div class="team-panel">
            <div class="team-panel-title">Our Team</div>
            {team_html}
        </div>
        <div class="team-panel">
            <div class="team-panel-title">Project Advisor</div>
            <div class="advisor-card">
                <div class="advisor-avatar">NM</div>
                <div class="advisor-name">N.M. Masuldar</div>
                <div class="advisor-title">
                    Lecturer, Dept. of Computer Engineering<br>
                    Govt. Polytechnic, Chhatrapati Sambhajinagar
                </div>
                <div class="advisor-badge">Project Advisor</div>
                <div class="advisor-quote">
                    "Guiding the next generation of engineers to build
                    technology that is both meaningful and accessible."
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back to PromptML Studio", key="about_back_bottom"):
        st.session_state.current_page = "home"
        st.session_state.mode = None
        st.rerun()