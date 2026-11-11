
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================================
# 1. PAGE CONFIGURATION AND PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "dataset" / "employee_data.csv"

# ==========================================================
# 2. COLOUR THEME
# ==========================================================

BG = "#EFFFF2"
HEADER = "#91E3AF"
CARD = "#D0F5DC"
DARK = "#123B2A"
TEXT = "#234B38"
GREEN = "#26734D"
LIGHT_GREEN = "#91DDAF"
GRID = "#D7E7DC"
WHITE = "#F8FFF9"

# ==========================================================
# 3. CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #EFFFF2;
        color: #173D2D;
        font-family: Georgia, "Times New Roman", serif;
    }

    .block-container {
        padding-top: 0.7rem;
        padding-bottom: 1.5rem;
        max-width: 100%;
    }

    /* Main headings */

    h1, h2, h3, h4, h5, h6 {
        color: #103B29 !important;
        font-family: Georgia, "Times New Roman", serif !important;
        font-weight: bold !important;
    }

    p, label, li {
        color: #234B38 !important;
    }

    /* Dashboard header */

    .dashboard-header {
        background-color: #91E3AF;
        border-radius: 17px;
        text-align: center;
        padding: 15px 8px;
        margin-bottom: 15px;
        box-shadow: 0 3px 8px rgba(50,90,60,0.12);
    }

    .dashboard-header h1 {
        color: #103B29 !important;
        font-size: clamp(23px, 3vw, 36px);
        font-family: Georgia, "Times New Roman", serif;
        font-weight: bold;
        letter-spacing: 1px;
        margin: 0;
    }

    /* KPI cards */

    .kpi-card {
        background-color: #D0F5DC;
        border: 1.5px solid #668F75;
        border-radius: 16px;
        min-height: 105px;
        padding: 14px 6px;
        text-align: center;
        box-shadow: 4px 6px 10px rgba(45,80,55,0.15);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .kpi-value {
        color: #075B3B !important;
        font-size: clamp(23px, 2.4vw, 37px);
        font-family: Georgia, "Times New Roman", serif;
        font-weight: bold;
        line-height: 1.2;
    }

    .kpi-label {
        color: #234B38 !important;
        font-size: 13px;
        font-family: Georgia, "Times New Roman", serif;
        font-weight: bold;
        margin-top: 7px;
    }

    /* Filters */

    div[data-testid="stSelectbox"] {
        background-color: #D0F5DC;
        border: 1px solid #668F75;
        border-radius: 12px;
        padding: 5px 8px;
        box-shadow: 3px 5px 8px rgba(45,80,55,0.12);
    }

    div[data-testid="stSelectbox"] label {
        color: #173D2D !important;
        font-weight: bold;
    }

    /* Chart containers */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #F8FFF9;
        border: 1px solid #A3BBA8;
        border-radius: 10px;
        box-shadow: 3px 5px 9px rgba(45,80,55,0.10);
        padding: 5px;
    }

    /* Data tables */

    [data-testid="stDataFrame"] {
        border: 1px solid #A3BBA8;
        border-radius: 8px;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background-color: #D9F0E3;
    }

    [data-testid="stSidebar"] * {
        color: #123B2A;
    }

    /* Download button */

    .stDownloadButton button {
        background-color: #26734D;
        color: white !important;
        border-radius: 8px;
        border: none;
    }

    .stDownloadButton button p {
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# 4. LOAD DATASET
# ==========================================================

@st.cache_data
def load_data(path):

    data = pd.read_csv(path)

    data.columns = data.columns.str.strip()

    data["Attrition"] = (
        data["Attrition"]
        .astype(str)
        .str.strip()
        .str.capitalize()
    )

    data["Gender"] = (
        data["Gender"]
        .astype(str)
        .str.strip()
        .str.capitalize()
    )

    return data


if not DATA_PATH.exists():

    st.error("Employee dataset not found. Check dataset/employee_data.csv.")
    st.stop()

try:

    df = load_data(DATA_PATH)

except Exception as error:

    st.error(f"Dataset loading error: {error}")
    st.stop()

# ==========================================================
# 5. VALIDATE DATASET
# ==========================================================

required_columns = [
    "Age",
    "Gender",
    "Department",
    "JobRole",
    "Attrition",
    "MonthlyIncome"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(f"Missing dataset columns: {missing_columns}")
    st.stop()

# ==========================================================
# 6. DASHBOARD HEADER
# ==========================================================

st.markdown(
    """
    <div class="dashboard-header">
        <h1>HR ATTRITION DASHBOARD</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# 7. FILTER OPTIONS
# ==========================================================

gender_options = ["All"] + sorted(
    df["Gender"].dropna().unique().tolist()
)

department_options = ["All"] + sorted(
    df["Department"].dropna().unique().tolist()
)

# ==========================================================
# 8. FILTER INPUTS
# ==========================================================

f1, f2 = st.columns(2)

with f1:

    selected_gender = st.selectbox(
        "Gender",
        gender_options,
        key="dashboard_gender"
    )

with f2:

    selected_department = st.selectbox(
        "Department",
        department_options,
        key="dashboard_department"
    )

# ==========================================================
# 9. FILTER DATA
# ==========================================================

filtered = df.copy()

if selected_gender != "All":

    filtered = filtered[
        filtered["Gender"] == selected_gender
    ]

if selected_department != "All":

    filtered = filtered[
        filtered["Department"] == selected_department
    ]

if filtered.empty:

    st.warning("No employees found for the selected filters.")
    st.stop()

# ==========================================================
# 10. KPI CALCULATIONS
# ==========================================================

total_employees = len(filtered)

active_employees = int(
    (filtered["Attrition"] == "No").sum()
)

employees_left = int(
    (filtered["Attrition"] == "Yes").sum()
)

attrition_rate = (
    employees_left / total_employees * 100
)

average_salary = filtered["MonthlyIncome"].mean()

department_count = filtered["Department"].nunique()

# ==========================================================
# 11. KPI CARD FUNCTION
# ==========================================================

def kpi_card(value, label):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# 12. DISPLAY KPI CARDS
# ==========================================================

st.write("")

k1, k2, k3, k4, k5 = st.columns(5, gap="small")

with k1:

    kpi_card(
        f"{total_employees:,}",
        "Total Employees"
    )

with k2:

    kpi_card(
        f"{active_employees:,}",
        "Active Employees"
    )

with k3:

    kpi_card(
        f"{attrition_rate:.1f}%",
        "Attrition Rate"
    )

with k4:

    kpi_card(
        f"{average_salary / 1000:.2f}K",
        "Average Salary"
    )

with k5:

    kpi_card(
        str(department_count),
        "Departments"
    )

st.write("")

# ==========================================================
# 13. COMMON CHART STYLE
# ==========================================================

def chart_style(fig, height=270):

    fig.update_layout(

        template="plotly_white",

        paper_bgcolor=WHITE,

        plot_bgcolor=WHITE,

        font=dict(
            family="Georgia, Times New Roman, serif",
            size=12,
            color=DARK
        ),

        title_font=dict(
            family="Georgia, Times New Roman, serif",
            size=16,
            color=DARK
        ),

        height=height,

        margin=dict(
            l=12,
            r=18,
            t=45,
            b=15
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            x=0,
            font=dict(
                size=11,
                color=DARK
            )
        )

    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#A3BBA8",
        tickfont=dict(color=DARK)
    )

    fig.update_yaxes(
        gridcolor=GRID,
        zeroline=False,
        linecolor="#A3BBA8",
        tickfont=dict(color=DARK)
    )

    return fig

# ==========================================================
# 14. DEPARTMENT AND GENDER CHART
# ==========================================================

department_gender = (
    filtered.groupby(
        ["Department", "Gender"]
    )
    .size()
    .reset_index(name="Employees")
)

fig1 = px.bar(

    department_gender,

    x="Employees",

    y="Department",

    color="Gender",

    orientation="h",

    barmode="group",

    text="Employees",

    color_discrete_map={
        "Female": "#4A514D",
        "Male": "#26734D"
    },

    title="Total Employees by Department and Gender"

)

fig1.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig1.update_layout(
    xaxis_title="",
    yaxis_title="",
    legend_title_text=""
)

fig1 = chart_style(fig1, 270)

# ==========================================================
# 15. JOB ROLE CHART
# ==========================================================

job_roles = (
    filtered["JobRole"]
    .value_counts()
    .reset_index()
)

job_roles.columns = [
    "Job Role",
    "Employees"
]

fig2 = px.bar(

    job_roles,

    x="Job Role",

    y="Employees",

    text="Employees",

    color="Employees",

    color_continuous_scale=[
        "#B5E5C2",
        "#588563",
        "#245A3C"
    ],

    title="Total Employees by Job Role"

)

fig2.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig2.update_layout(
    xaxis_title="",
    yaxis_title="",
    coloraxis_showscale=False
)

fig2.update_xaxes(
    tickangle=-30,
    tickfont=dict(size=9, color=DARK)
)

fig2 = chart_style(fig2, 270)

# ==========================================================
# 16. AGE AND GENDER CHART
# ==========================================================

age_data = filtered.copy()

age_data["Age Group"] = pd.cut(

    age_data["Age"],

    bins=[17, 24, 34, 44, 54, 100],

    labels=[
        "18-24",
        "25-34",
        "35-44",
        "45-54",
        "55 and above"
    ]

)

age_gender = (
    age_data.groupby(
        ["Age Group", "Gender"],
        observed=False
    )
    .size()
    .reset_index(name="Employees")
)

fig3 = px.bar(

    age_gender,

    x="Age Group",

    y="Employees",

    color="Gender",

    barmode="group",

    color_discrete_map={
        "Female": "#4A514D",
        "Male": "#26734D"
    },

    title="Total Employees by Age and Gender"

)

fig3.update_layout(
    xaxis_title="",
    yaxis_title="",
    legend_title_text=""
)

fig3 = chart_style(fig3, 270)

# ==========================================================
# 17. ATTRITION DISTRIBUTION DONUT
# ==========================================================

attrition_data = (
    filtered["Attrition"]
    .value_counts()
    .reindex(["No", "Yes"], fill_value=0)
    .rename_axis("Status")
    .reset_index(name="Employees")
)

attrition_data["Status"] = attrition_data["Status"].map({
    "No": "Active",
    "Yes": "Left"
})

fig4 = px.pie(

    attrition_data,

    names="Status",

    values="Employees",

    hole=0.58,

    color="Status",

    color_discrete_map={
        "Active": "#4A514D",
        "Left": "#91DDAF"
    },

    title="Employee Attrition Distribution"

)

fig4.update_traces(
    textposition="outside",
    textinfo="value",
    textfont=dict(color=DARK)
)

fig4.update_layout(
    legend_title_text=""
)

fig4 = chart_style(fig4, 270)

# ==========================================================
# 18. ATTRITION BY GENDER DONUT
# ==========================================================

gender_attrition = filtered[
    filtered["Attrition"] == "Yes"
]

gender_counts = (
    gender_attrition["Gender"]
    .value_counts()
    .rename_axis("Gender")
    .reset_index(name="Employees")
)

fig5 = px.pie(

    gender_counts,

    names="Gender",

    values="Employees",

    hole=0.58,

    color="Gender",

    color_discrete_map={
        "Male": "#4A514D",
        "Female": "#91DDAF"
    },

    title="Attrition by Gender"

)

fig5.update_traces(
    textposition="outside",
    textinfo="value",
    textfont=dict(color=DARK)
)

fig5.update_layout(
    legend_title_text=""
)

fig5 = chart_style(fig5, 270)

# ==========================================================
# 19. DISPLAY CHARTS
# ==========================================================

# First row

left, right = st.columns(2, gap="small")

with left:

    with st.container(border=True):

        st.plotly_chart(
            fig1,
            use_container_width=True,
            config={"displayModeBar": False}
        )

with right:

    with st.container(border=True):

        st.plotly_chart(
            fig2,
            use_container_width=True,
            config={"displayModeBar": False}
        )

# Second row

left, right = st.columns(2, gap="small")

with left:

    with st.container(border=True):

        st.plotly_chart(
            fig3,
            use_container_width=True,
            config={"displayModeBar": False}
        )

with right:

    donut1, donut2 = st.columns(2, gap="small")

    with donut1:

        with st.container(border=True):

            st.plotly_chart(
                fig4,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with donut2:

        with st.container(border=True):

            st.plotly_chart(
                fig5,
                use_container_width=True,
                config={"displayModeBar": False}
            )

# ==========================================================
# 20. DETAILED WORKFORCE SUMMARY
# ==========================================================

with st.expander("View Detailed Workforce Summary"):

    summary = (
        filtered.groupby("Department")
        .agg(
            Total_Employees=("Attrition", "size"),

            Active_Employees=(
                "Attrition",
                lambda x: (x == "No").sum()
            ),

            Employees_Left=(
                "Attrition",
                lambda x: (x == "Yes").sum()
            )
        )
        .reset_index()
    )

    summary["Attrition Rate"] = (
        summary["Employees_Left"]
        / summary["Total_Employees"] * 100
    )

    st.dataframe(
        summary.style.format({
            "Attrition Rate": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Workforce Summary",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="workforce_summary.csv",
        mime="text/csv"
    )

# ==========================================================
# 21. FOOTER
# ==========================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align: center;
        color: #315B45;
        font-family: Georgia, serif;
        font-size: 13px;
        padding: 15px;
    ">
        <strong>HR ATTRITION DASHBOARD</strong>
        <br><br>
        Employee Attrition Prediction and Workforce Analytics
        <br>
        Data Science and Machine Learning Project
    </div>
    """,
    unsafe_allow_html=True
)
