"""
PromptML Studio - Contact Page
"""
import streamlit as st


def show_contact_page():
    """Render the Contact page"""

    def go_home():
        st.session_state.current_page = "home"
        st.session_state.mode = None
        st.query_params.clear()
        st.rerun()

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
    .contact-hero { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); border-radius: 16px; padding: 56px 48px; text-align: center; margin-bottom: 36px; position: relative; overflow: hidden; }
    .contact-hero-label { font-family: 'Inter', sans-serif; font-size: 0.72rem; font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase; color: #8899ee; margin-bottom: 14px; }
    .contact-hero-title { font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 30%, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 18px; line-height: 1.15; }
    .contact-hero-sub { font-family: 'Inter', sans-serif; font-size: 1rem; color: rgba(255,255,255,0.6); max-width: 520px; margin: 0 auto; line-height: 1.7; }
    .contact-section-title { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 6px; margin-top: 8px; }
    .contact-section-line { width: 44px; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 2px; margin-bottom: 24px; }
    .info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 36px; }
    .info-card { background: #13132a; border: 1px solid rgba(102,126,234,0.15); border-radius: 14px; padding: 28px 22px; position: relative; text-align: center; }
    .info-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 14px 14px 0 0; opacity: 0.7; }
    .info-icon { font-size: 1.8rem; margin-bottom: 12px; }
    .info-label { font-family: 'Inter', sans-serif; font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: #667eea; margin-bottom: 8px; }
    .info-value { font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 600; color: #ddd; margin-bottom: 4px; line-height: 1.4; }
    .info-sub { font-family: 'Inter', sans-serif; font-size: 0.78rem; color: #555; line-height: 1.5; }
    .info-link { color: #8899ee; text-decoration: none; font-family: 'Outfit', sans-serif; font-size: 0.92rem; font-weight: 600; }
    .info-link:hover { color: #c5caff; }
    .quote-box { background: #16162a; border: 1px solid rgba(102,126,234,0.15); border-left: 3px solid #667eea; border-radius: 12px; padding: 22px 28px; margin-bottom: 32px; font-family: 'Inter', sans-serif; font-size: 0.92rem; color: #b0b0c8; line-height: 1.8; font-style: italic; }
    .quote-box strong { color: #c5caff; font-style: normal; }
    .cases-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 36px; }
    .case-card { background: #13132a; border: 1px solid rgba(102,126,234,0.12); border-radius: 12px; padding: 22px 18px; position: relative; }
    .case-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 12px 12px 0 0; }
    .case-card.red::before { background: linear-gradient(90deg, #e96c6c, #c0392b); }
    .case-card.green::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
    .case-card.purple::before { background: linear-gradient(90deg, #667eea, #764ba2); }
    .case-icon { font-size: 1.5rem; margin-bottom: 10px; }
    .case-title { font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 600; color: #ddd; margin-bottom: 7px; }
    .case-desc { font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #666; line-height: 1.6; }
    div[data-testid="stButton"].back-btn > button { background: rgba(102,126,234,0.1) !important; border: 1px solid rgba(102,126,234,0.3) !important; color: #8899ee !important; font-size: 0.85rem !important; font-family: 'Inter', sans-serif !important; border-radius: 8px !important; padding: 6px 16px !important; }
    div[data-testid="stButton"].back-btn > button:hover { background: rgba(102,126,234,0.2) !important; color: #c5caff !important; transform: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Top Back Button
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="contact_back_top"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Hero
    st.markdown('<div class="contact-hero"><div class="contact-hero-label">Support</div><div class="contact-hero-title">Get in Touch</div><div class="contact-hero-sub">Have a question, feedback, or partnership idea? We are here to help. Reach out and we will get back to you as soon as possible.</div></div>', unsafe_allow_html=True)

    # Contact Info Cards
    st.markdown('<div class="contact-section-title">Contact Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="contact-section-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-grid"><div class="info-card"><div class="info-icon">&#x2709;</div><div class="info-label">Email</div><a class="info-link" href="mailto:promptmlstudio@gmail.com">promptmlstudio@gmail.com</a><div class="info-sub">We respond within 24 hours on working days</div></div><div class="info-card"><div class="info-icon">&#x1F4CD;</div><div class="info-label">Location</div><div class="info-value">Chhatrapati Sambhajinagar</div><div class="info-sub">Maharashtra, India</div></div><div class="info-card"><div class="info-icon">&#x1F552;</div><div class="info-label">Support Hours</div><div class="info-value">Monday &#x2013; Saturday</div><div class="info-sub">10:00 AM &#x2013; 6:00 PM IST</div></div></div>', unsafe_allow_html=True)

    # Quote
    st.markdown('<div class="quote-box">At <strong>PromptML Studio</strong>, we believe machine learning should be accessible to every student and professional. Your queries, feedback, and suggestions help us improve the platform every single day &#x2014; every message matters to us.</div>', unsafe_allow_html=True)

    # Contact Cases
    st.markdown('<div class="contact-section-title">Contact Us For</div>', unsafe_allow_html=True)
    st.markdown('<div class="contact-section-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="cases-grid"><div class="case-card red"><div class="case-icon">&#x1F6A8;</div><div class="case-title">Report a Bug</div><div class="case-desc">Encountered an error during model training, PDF generation, or deployment? Let us know and we will fix it immediately.</div></div><div class="case-card green"><div class="case-icon">&#x1F91D;</div><div class="case-title">Partnership Opportunities</div><div class="case-desc">Interested in collaborating with PromptML Studio for a project, event, or integration? We are open to building together.</div></div><div class="case-card purple"><div class="case-icon">&#x1F6E0;</div><div class="case-title">Technical Support</div><div class="case-desc">Facing issues with file upload, model results, or website deployment? Our team is ready to guide you step by step.</div></div><div class="case-card purple"><div class="case-icon">&#x1F4A1;</div><div class="case-title">Feature Requests</div><div class="case-desc">Have an idea for a new feature or improvement? Share it with us &#x2014; many of our best features came from user feedback.</div></div><div class="case-card green"><div class="case-icon">&#x1F393;</div><div class="case-title">Academic Enquiries</div><div class="case-desc">Using PromptML Studio for a college project or thesis? Contact us for guidance, references, or project support.</div></div><div class="case-card red"><div class="case-icon">&#x1F4DD;</div><div class="case-title">General Feedback</div><div class="case-desc">Any other comments, suggestions, or appreciation? We read every message and use your feedback to grow.</div></div></div>', unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)

    # Bottom Back Button
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to PromptML Studio", key="contact_back_bottom"):
        go_home()
    st.markdown('</div>', unsafe_allow_html=True)