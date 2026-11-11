
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================



BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "dataset" / "employee_data.csv"

# =====================================================
# 2. CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

[data-testid="stSidebar"] {
    background-color: #14243B;
}

[data-testid="stSidebar"] * {
    color: white;
}

.main-heading {
    font-size: 32px;
    font-weight: 800;
    color: #14243B;
}

.sub-heading {
    color: #718096;
    font-size: 15px;
    margin-bottom: 25px;
}

.section-heading {
    font-size: 21px;
    font-weight: 750;
    color: #14243B;
    margin-top: 20px;
    margin-bottom: 15px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. HEADER
# =====================================================

st.markdown(
    '<div class="main-heading">'
    '💡 Employee Retention Intelligence'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-heading">'
    'Data-driven workforce recommendations and employee retention strategies'
    '</div>',
    unsafe_allow_html=True
)

# =====================================================
# 4. LOAD DATASET
# =====================================================

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()


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

    return data


try:
    df = load_data(str(DATA_PATH))
except Exception as error:
    st.error(f"Dataset loading error: {error}")
    st.stop()


# =====================================================
# 5. FILTERS
# =====================================================

st.markdown(
    '<div class="section-heading">Workforce Filters</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    departments = ["All"] + sorted(
        df["Department"].dropna().unique().tolist()
    )

    selected_department = st.selectbox(
        "Select Department",
        departments
    )

with col2:
    if selected_department == "All":
        role_data = df
    else:
        role_data = df[
            df["Department"] == selected_department
        ]

    roles = ["All"] + sorted(
        role_data["JobRole"].dropna().unique().tolist()
    )

    selected_role = st.selectbox(
        "Select Job Role",
        roles
    )

filtered = df.copy()

if selected_department != "All":
    filtered = filtered[
        filtered["Department"] == selected_department
    ]

if selected_role != "All":
    filtered = filtered[
        filtered["JobRole"] == selected_role
    ]

if filtered.empty:
    st.warning("No employee records match these filters.")
    st.stop()

# =====================================================
# 6. WORKFORCE SUMMARY
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">Retention Overview</div>',
    unsafe_allow_html=True
)

total = len(filtered)

left = int(
    (filtered["Attrition"] == "Yes").sum()
)

retained = int(
    (filtered["Attrition"] == "No").sum()
)

attrition_rate = (
    left / total * 100 if total else 0
)

retention_rate = (
    retained / total * 100 if total else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Employees", f"{total:,}")
c2.metric("Employees Left", f"{left:,}")
c3.metric("Employees Retained", f"{retained:,}")
c4.metric("Attrition Rate", f"{attrition_rate:.2f}%")

# =====================================================
# 7. DEPARTMENT ATTRITION ANALYSIS
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">Department-wise Retention Analysis</div>',
    unsafe_allow_html=True
)

department_analysis = (
    df.groupby("Department")
    .agg(
        Total_Employees=("Attrition", "size"),
        Employees_Left=(
            "Attrition",
            lambda x: (x == "Yes").sum()
        )
    )
    .reset_index()
)

department_analysis["Attrition Rate"] = (
    department_analysis["Employees_Left"]
    / department_analysis["Total_Employees"] * 100
)

fig1 = px.bar(
    department_analysis,
    x="Department",
    y="Attrition Rate",
    color="Department",
    text_auto=".2f",
    title="Attrition Rate Across Departments",
    color_discrete_sequence=[
        "#2563EB",
        "#0EA5E9",
        "#6366F1"
    ]
)

fig1.update_layout(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=380,
    yaxis_title="Attrition Rate (%)"
)

st.plotly_chart(fig1, use_container_width=True)

st.dataframe(
    department_analysis.style.format({
        "Attrition Rate": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)

# =====================================================
# 8. OVERTIME ANALYSIS
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">Overtime Management</div>',
    unsafe_allow_html=True
)

if "OverTime" in filtered.columns:

    overtime_analysis = (
        filtered.groupby("OverTime")
        .agg(
            Employees=("Attrition", "size"),
            Employees_Left=(
                "Attrition",
                lambda x: (x == "Yes").sum()
            )
        )
        .reset_index()
    )

    overtime_analysis["Attrition Rate"] = (
        overtime_analysis["Employees_Left"]
        / overtime_analysis["Employees"] * 100
    )

    col1, col2 = st.columns(2)

    with col1:

        fig2 = px.bar(
            overtime_analysis,
            x="OverTime",
            y="Attrition Rate",
            color="OverTime",
            text_auto=".2f",
            title="Overtime vs Attrition",
            color_discrete_map={
                "Yes": "#EF4444",
                "No": "#2563EB"
            }
        )

        fig2.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            height=350
        )

        st.plotly_chart(fig2, use_container_width=True)

    with col2:

        for _, row in overtime_analysis.iterrows():

            st.metric(
                f"{row['OverTime']} Overtime Attrition",
                f"{row['Attrition Rate']:.2f}%",
                f"{int(row['Employees_Left'])} employees left"
            )

# =====================================================
# 9. JOB SATISFACTION ANALYSIS
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">Employee Satisfaction Analysis</div>',
    unsafe_allow_html=True
)

if "JobSatisfaction" in filtered.columns:

    satisfaction_analysis = (
        filtered.groupby("JobSatisfaction")
        .agg(
            Employees=("Attrition", "size"),
            Employees_Left=(
                "Attrition",
                lambda x: (x == "Yes").sum()
            )
        )
        .reset_index()
    )

    satisfaction_analysis["Attrition Rate"] = (
        satisfaction_analysis["Employees_Left"]
        / satisfaction_analysis["Employees"] * 100
    )

    fig3 = px.bar(
        satisfaction_analysis,
        x="JobSatisfaction",
        y="Attrition Rate",
        color="Attrition Rate",
        text_auto=".2f",
        title="Job Satisfaction and Employee Attrition",
        color_continuous_scale="Blues"
    )

    fig3.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=370,
        xaxis_title="Job Satisfaction Level",
        yaxis_title="Attrition Rate (%)"
    )

    st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# 10. CAREER DEVELOPMENT ANALYSIS
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">Career Development Analysis</div>',
    unsafe_allow_html=True
)

if "YearsSinceLastPromotion" in filtered.columns:

    promotion_analysis = filtered.copy()

    promotion_analysis["Promotion Group"] = pd.cut(
        promotion_analysis["YearsSinceLastPromotion"],
        bins=[-1, 1, 3, 5, float("inf")],
        labels=[
            "0–1 Years",
            "2–3 Years",
            "4–5 Years",
            "More than 5 Years"
        ]
    )

    promotion_data = (
        promotion_analysis.groupby(
            "Promotion Group",
            observed=False
        )["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Attrition Rate")
    )

    fig4 = px.bar(
        promotion_data,
        x="Promotion Group",
        y="Attrition Rate",
        color="Promotion Group",
        text_auto=".2f",
        title="Promotion Gap vs Attrition",
        color_discrete_sequence=px.colors.sequential.Blues
    )

    fig4.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=370,
        yaxis_title="Attrition Rate (%)"
    )

    st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# 11. WORK-LIFE BALANCE
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">Work-Life Balance Analysis</div>',
    unsafe_allow_html=True
)

if "WorkLifeBalance" in filtered.columns:

    balance_data = (
        filtered.groupby("WorkLifeBalance")
        .agg(
            Employees=("Attrition", "size"),
            Employees_Left=(
                "Attrition",
                lambda x: (x == "Yes").sum()
            )
        )
        .reset_index()
    )

    balance_data["Attrition Rate"] = (
        balance_data["Employees_Left"]
        / balance_data["Employees"] * 100
    )

    fig5 = px.bar(
        balance_data,
        x="WorkLifeBalance",
        y="Attrition Rate",
        color="Attrition Rate",
        text_auto=".2f",
        title="Work-Life Balance vs Attrition",
        color_continuous_scale="Teal"
    )

    fig5.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=350
    )

    st.plotly_chart(fig5, use_container_width=True)

# =====================================================
# 12. GENERATE HR RECOMMENDATIONS
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">'
    'AI-Assisted HR Retention Recommendations'
    '</div>',
    unsafe_allow_html=True
)

recommendations = []


def add_recommendation(title, priority, observation, action):

    recommendations.append({
        "Area": title,
        "Priority": priority,
        "Observed Pattern": observation,
        "Recommended HR Action": action
    })


# Overtime
if "OverTime" in filtered.columns:

    overtime_yes = filtered[
        filtered["OverTime"] == "Yes"
    ]

    overtime_no = filtered[
        filtered["OverTime"] == "No"
    ]

    if len(overtime_yes) >= 5 and len(overtime_no) >= 5:

        yes_rate = (
            overtime_yes["Attrition"] == "Yes"
        ).mean() * 100

        no_rate = (
            overtime_no["Attrition"] == "Yes"
        ).mean() * 100

        if yes_rate > no_rate:

            add_recommendation(
                "Overtime Management",
                "High",
                f"Overtime group attrition is {yes_rate:.2f}%, "
                f"compared with {no_rate:.2f}% for non-overtime employees.",
                "Review workload distribution, staffing levels "
                "and overtime scheduling."
            )


# Job satisfaction
if "JobSatisfaction" in filtered.columns:

    low = filtered[
        filtered["JobSatisfaction"] <= 2
    ]

    high = filtered[
        filtered["JobSatisfaction"] >= 3
    ]

    if len(low) >= 5 and len(high) >= 5:

        low_rate = (
            low["Attrition"] == "Yes"
        ).mean() * 100

        high_rate = (
            high["Attrition"] == "Yes"
        ).mean() * 100

        if low_rate > high_rate:

            add_recommendation(
                "Employee Satisfaction",
                "High",
                f"Lower satisfaction group attrition: {low_rate:.2f}%.",
                "Conduct confidential feedback sessions, "
                "review workplace concerns and develop "
                "employee engagement programmes."
            )


# Promotion
if "YearsSinceLastPromotion" in filtered.columns:

    delayed = filtered[
        filtered["YearsSinceLastPromotion"] >= 4
    ]

    recent = filtered[
        filtered["YearsSinceLastPromotion"] < 4
    ]

    if len(delayed) >= 5 and len(recent) >= 5:

        delayed_rate = (
            delayed["Attrition"] == "Yes"
        ).mean() * 100

        recent_rate = (
            recent["Attrition"] == "Yes"
        ).mean() * 100

        if delayed_rate > recent_rate:

            add_recommendation(
                "Career Progression",
                "Medium",
                f"Employees with longer promotion gaps have "
                f"{delayed_rate:.2f}% observed attrition.",
                "Review career progression pathways, mentorship "
                "and professional development opportunities."
            )


# Work-life balance
if "WorkLifeBalance" in filtered.columns:

    poor_balance = filtered[
        filtered["WorkLifeBalance"] <= 2
    ]

    good_balance = filtered[
        filtered["WorkLifeBalance"] >= 3
    ]

    if len(poor_balance) >= 5 and len(good_balance) >= 5:

        poor_rate = (
            poor_balance["Attrition"] == "Yes"
        ).mean() * 100

        good_rate = (
            good_balance["Attrition"] == "Yes"
        ).mean() * 100

        if poor_rate > good_rate:

            add_recommendation(
                "Work-Life Balance",
                "Medium",
                f"Lower work-life balance group attrition: {poor_rate:.2f}%.",
                "Review workload expectations and consider "
                "flexible working arrangements."
            )


# Department analysis
if selected_department == "All" and len(department_analysis) > 0:

    highest = department_analysis.loc[
        department_analysis["Attrition Rate"].idxmax()
    ]

    add_recommendation(
        "Department Workforce Planning",
        "High",
        f"{highest['Department']} has the highest observed "
        f"department attrition rate at "
        f"{highest['Attrition Rate']:.2f}%.",
        "Conduct a department-level workforce review, "
        "including workload, leadership, employee feedback "
        "and career development."
    )


if recommendations:

    for index, rec in enumerate(recommendations, start=1):

        with st.expander(
            f"{index}. {rec['Area']} — {rec['Priority']} Priority"
        ):

            st.write("**Observed Pattern**")
            st.write(rec["Observed Pattern"])

            st.write("**Recommended Action**")
            st.write(rec["Recommended HR Action"])

else:

    st.info(
        "No recommendation triggers were met for the current "
        "filtered data. This does not establish that attrition "
        "risks are absent."
    )

# =====================================================
# 13. DOWNLOAD HR REPORT
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">Download HR Retention Report</div>',
    unsafe_allow_html=True
)

report_df = pd.DataFrame(recommendations)

if not report_df.empty:

    report_df.insert(
        0,
        "Department Filter",
        selected_department
    )

    report_df.insert(
        1,
        "Job Role Filter",
        selected_role
    )

    report_df.insert(
        2,
        "Employees Analysed",
        total
    )

    csv_data = report_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download HR Recommendations CSV",
        data=csv_data,
        file_name="employee_retention_recommendations.csv",
        mime="text/csv",
        use_container_width=True
    )

else:

    st.info("No generated recommendations to export.")

# =====================================================
# 14. DISCLAIMER
# =====================================================

st.caption(
    "Recommendations are generated from descriptive patterns "
    "in the sample dataset. They do not establish causation. "
    "HR teams should validate findings with employee feedback "
    "and organizational context before taking action."
)

# =====================================================
# 15. FOOTER
# =====================================================

st.divider()

st.markdown("""
<div style="text-align:center;color:#718096;
font-size:12px;padding:20px;">

<b>EMPLOYEE INTELLIGENCE</b><br><br>

Employee Retention & Workforce Strategy<br>

Data Science and Machine Learning Project

</div>
""", unsafe_allow_html=True)
