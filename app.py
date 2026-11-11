import streamlit as st
import textwrap

# =====================================================
# 1. APPLICATION CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Employee Intelligence",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. GLOBAL THEME
# =====================================================
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #EFFFF2;
    color: #173D2D;
    font-family: Georgia, "Times New Roman", serif;
}
html, body, p, li, label, span, div {
    font-family: Georgia, "Times New Roman", serif;
}
h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] p {
    color: #103B29;
}
[data-testid="stSidebar"] {
    background-color: #D9F0E3;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #123B2A;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 100%;
}
[data-testid="stMetricValue"] {
    color: #075B3B !important;
    font-weight: 800 !important;
}
[data-testid="stMetricLabel"] {
    color: #285B43 !important;
    font-weight: 600 !important;
}
[data-testid="stWidgetLabel"] {
    color: #173D2D !important;
    font-weight: 600 !important;
}
a { color: #087A50 !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. SIDEBAR BRANDING
# =====================================================
with st.sidebar:
    brand_html = textwrap.dedent("""
    <div style="padding:15px 0 20px 0;">
        <h2 style="color:#176B45; margin:0;">👥 Employee</h2>
        <h2 style="color:#123B2A; margin:0;">Intelligence</h2>
        <p style="font-size:13px; color:#315B45; margin-top:8px;">
            AI Powered HR Analytics
        </p>
    </div>
    """)
    st.markdown(brand_html, unsafe_allow_html=True)
    st.divider()
    st.caption("EMPLOYEE WORKFORCE PLATFORM")
    st.write("")
    st.info(
        "Explore workforce analytics, predict employee attrition "
        "and discover employee retention insights."
    )
    footer_html = textwrap.dedent("""
    <div style="font-size:12px; color:#315B45; line-height:1.6;">
        Employee Attrition Prediction<br>
        &amp; Workforce Analytics Using ML
    </div>
    """)
    st.markdown(footer_html, unsafe_allow_html=True)

# =====================================================
# 4. CENTRALIZED NAVIGATION
# =====================================================
pages = {
    "EMPLOYEE INTELLIGENCE": [
        st.Page("pages/1_Dashboard.py", title="Dashboard", icon="🏠", default=True),
        st.Page("pages/2_Workforce_Analytics.py", title="Workforce Analytics", icon="📊"),
        st.Page("pages/3_Attrition_Prediction.py", title="Attrition Prediction", icon="🤖"),
        st.Page("pages/4_AI_Insights.py", title="AI Insights", icon="🧠"),
        st.Page("pages/5_Retention_Recommendations.py", title="Retention Recommendations", icon="💡"),
        st.Page("pages/6_Employee_Explorer.py", title="Employee Explorer", icon="👥"),
        st.Page("pages/7_Model_Performance.py", title="Model Performance", icon="📈"),
    ]
}

navigation = st.navigation(pages, position="sidebar")
navigation.run()
