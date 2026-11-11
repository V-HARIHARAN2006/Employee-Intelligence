
import streamlit as st

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

.stApp {
    background-color: #EFFFF2;
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
}

[data-testid="stSidebar"] {
    background-color: #D0F5DC;
}

[data-testid="stSidebar"] * {
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 100%;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. SIDEBAR BRANDING
# =====================================================

with st.sidebar:

    st.markdown("""
    <div style="padding:15px 0 20px 0;">

        <h2 style="color:#588563;margin-bottom:0;">
            👥 Employee
        </h2>

        <h2 style="color:#3D4841;margin-top:0;">
            Intelligence
        </h2>

        <p style="font-size:13px;color:#718477;">
            AI Powered HR Analytics
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.caption("EMPLOYEE WORKFORCE PLATFORM")

    st.write("")

    st.info(
        "Explore workforce analytics, "
        "predict employee attrition and "
        "discover employee retention insights."
    )

    st.divider()

    st.markdown("""
    <div style="font-size:12px;color:#718477;">
        Employee Attrition Prediction<br>
        & Workforce Analytics Using ML
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 4. CENTRALIZED NAVIGATION
# =====================================================

pages = {

    "EMPLOYEE INTELLIGENCE": [

        st.Page(
            "pages/1_Dashboard.py",
            title="Dashboard",
            icon="🏠",
            default=True
        ),

        st.Page(
            "pages/2_Workforce_Analytics.py",
            title="Workforce Analytics",
            icon="📊"
        ),

        st.Page(
            "pages/3_Attrition_Prediction.py",
            title="Attrition Prediction",
            icon="🤖"
        ),

        st.Page(
            "pages/4_AI_Insights.py",
            title="AI Insights",
            icon="🧠"
        ),

        st.Page(
            "pages/5_Retention_Recommendations.py",
            title="Retention Recommendations",
            icon="💡"
        ),

        st.Page(
            "pages/6_Employee_Explorer.py",
            title="Employee Explorer",
            icon="👥"
        ),

        st.Page(
            "pages/7_Model_Performance.py",
            title="Model Performance",
            icon="📈"
        )

    ]

}

# =====================================================
# 5. RUN NAVIGATION
# =====================================================

navigation = st.navigation(
    pages,
    position="sidebar"
)

navigation.run()
