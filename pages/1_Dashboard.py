
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================================
# 1. PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "dataset" / "employee_data.csv"

# ==========================================================
# 2. COLOR THEME
# ==========================================================

BG = "#EFFFF2"
HEADER = "#91E3AF"
CARD = "#D0F5DC"
DARK = "#3D4841"
GREEN = "#588563"
LIGHT_GREEN = "#91DDAF"
GRID = "#D7E7DC"

# ==========================================================
# 3. CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.stApp {
    background-color: #EFFFF2;
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
}

.block-container {
    padding-top: 0.4rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

.dashboard-header {
    background-color: #91E3AF;
    border-radius: 17px;
    text-align: center;
    padding: 10px 8px;
    margin-bottom: 13px;
    box-shadow: 0 3px 8px rgba(50,90,60,0.12);
}

.dashboard-header h1 {
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(23px, 3vw, 36px);
    font-weight: bold;
    letter-spacing: 1px;
    margin: 0;
}

.kpi-card {
    background-color: #D0F5DC;
    border: 1.4px solid #668F75;
    border-radius: 16px;
    min-height: 100px;
    padding: 10px 5px;
    text-align: center;
    box-shadow: 4px 6px 10px rgba(45,80,55,0.20);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.kpi-value {
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(23px, 2.4vw, 37px);
    font-weight: bold;
    line-height: 1.2;
}

.kpi-label {
    color: #40554A;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 12px;
    font-weight: bold;
    margin-top: 5px;
}

.chart-title {
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 16px;
    margin-bottom: 4px;
}

div[data-testid="stSelectbox"] {
    background-color: #D0F5DC;
    border: 1px solid #668F75;
    border-radius: 12px;
    padding: 5px 8px;
    box-shadow: 3px 5px 8px rgba(45,80,55,0.12);
}

div[data-testid="stSelectbox"] label {
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
    font-weight: bold;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #F6FFF7;
    border: 1px solid #A3BBA8;
    border-radius: 9px;
    box-shadow: 3px 5px 9px rgba(45,80,55,0.12);
    padding: 4px;
}

</style>
""", unsafe_allow_html=True)

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

    st.error("Employee dataset not found.")

    st.code(str(DATA_PATH))

    st.stop()


try:

    df = load_data(str(DATA_PATH))

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

    st.error(
        f"Missing dataset columns: {missing_columns}"
    )

    st.stop()


# ==========================================================
# 6. DASHBOARD HEADER
# ==========================================================

st.markdown("""
<div class="dashboard-header">
    <h1>HR ATTRITION DASHBOARD</h1>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# 7. FILTERS
# ==========================================================

# Keep both filters in the same KPI row.

gender_options = ["All"] + sorted(
    df["Gender"].dropna().unique().tolist()
)

department_options = ["All"] + sorted(
    df["Department"].dropna().unique().tolist()
)

# ==========================================================
# 8. FILTER INPUTS
# ==========================================================

# Temporary default values are replaced by actual
# selections in the filter columns below.

gender_filter = "All"
department_filter = "All"

# ==========================================================
# 9. CALCULATE FILTERED DATA
# ==========================================================

# Use a compact filter row before KPI rendering.

f1, f2 = st.columns([1, 1])

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

    st.warning("No employees found for selected filters.")

    st.stop()


# ==========================================================
# 10. KPI VALUES
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

            <div class="kpi-value">
                {value}
            </div>

            <div class="kpi-label">
                {label}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# 12. DISPLAY KPI CARDS
# ==========================================================

st.write("")

k1, k2, k3, k4, k5 = st.columns(5)

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

def chart_style(fig, height=245):

    fig.update_layout(

        template="plotly_white",

        paper_bgcolor="#F6FFF7",

        plot_bgcolor="#F6FFF7",

        font=dict(
            family="Georgia, Times New Roman, serif",
            size=11,
            color="#3D4841"
        ),

        title_font=dict(
            family="Georgia, Times New Roman, serif",
            size=15,
            color="#3D4841"
        ),

        height=height,

        margin=dict(
            l=8,
            r=8,
            t=40,
            b=8
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            x=0,
            font=dict(size=10)
        )

    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#B6C9BA"
    )

    fig.update_yaxes(
        gridcolor="#E0ECE2",
        zeroline=False,
        linecolor="#B6C9BA"
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
        "Male": "#588563"
    },

    title="Total employees by Department and Gender"

)

fig1.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig1.update_layout(
    xaxis_title="",
    yaxis_title="",
    height=245,
    legend_title_text=""
)

fig1 = chart_style(fig1, 245)


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
        "#A7D9B3",
        "#588563",
        "#3F694B"
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
    coloraxis_showscale=False,
    height=245
)

fig2.update_xaxes(
    tickangle=-30,
    tickfont=dict(size=9)
)

fig2 = chart_style(fig2, 245)


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
        "Male": "#588563"
    },

    title="Total employees by Age and Gender"

)

fig3.update_layout(
    xaxis_title="",
    yaxis_title="",
    height=245,
    legend_title_text=""
)

fig3 = chart_style(fig3, 245)


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
    textinfo="value"
)

fig4.update_layout(
    height=245,
    legend_title_text=""
)

fig4 = chart_style(fig4, 245)


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
    textinfo="value"
)

fig5.update_layout(
    height=245,
    legend_title_text=""
)

fig5 = chart_style(fig5, 245)


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

st.markdown("""
<div style="
    text-align:center;
    color:#718477;
    font-family:Georgia,serif;
    font-size:12px;
    padding:15px;
">

    HR ATTRITION DASHBOARD<br><br>

    Employee Attrition Prediction and Workforce Analytics<br>

    Data Science and Machine Learning Project

</div>
""", unsafe_allow_html=True)
