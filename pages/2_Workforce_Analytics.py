import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.title("📊 Workforce Analytics")
st.caption("Analyze employee trends and attrition patterns")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "dataset" / "employee_data.csv"

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip()
    for col in ["Attrition", "Gender", "OverTime"]:
        if col in data.columns:
            data[col] = data[col].astype(str).str.strip()
    return data

if not DATA_PATH.exists():
    st.error("Employee dataset not found. Check dataset/employee_data.csv.")
    st.stop()

try:
    df = load_data(DATA_PATH)
except Exception as error:
    st.error(f"Could not load employee dataset: {error}")
    st.stop()

required = ["Attrition", "Department", "MonthlyIncome", "OverTime", "JobSatisfaction"]
missing = [column for column in required if column not in df.columns]
if missing:
    st.error(f"Dataset is missing required columns: {', '.join(missing)}")
    st.stop()

# Consistent high-contrast Plotly styling
CHART_FONT = dict(family="Georgia, Times New Roman, serif", color="#173D2D", size=13)
PLOT_BG = "#F6FFF7"

def style_chart(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=CHART_FONT,
        title_font=dict(family="Georgia, Times New Roman, serif", color="#103B29", size=18),
        height=height,
        margin=dict(l=20, r=20, t=65, b=35),
        legend_title_font=dict(color="#173D2D"),
    )
    fig.update_xaxes(tickfont=dict(color="#234B38"), title_font=dict(color="#173D2D"),
                     gridcolor="#DCEBE0", zeroline=False)
    fig.update_yaxes(tickfont=dict(color="#234B38"), title_font=dict(color="#173D2D"),
                     gridcolor="#DCEBE0", zeroline=False)
    return fig

# Attrition distribution
st.subheader("Employee Attrition Distribution")
attrition_counts = df["Attrition"].value_counts().rename_axis("Attrition").reset_index(name="Employees")
fig1 = px.pie(
    attrition_counts, names="Attrition", values="Employees", hole=0.55,
    title="Employees: Stayed vs Left",
    color="Attrition",
    color_discrete_map={"No": "#176B45", "Yes": "#91DDAF"}
)
fig1.update_traces(textposition="inside", textinfo="label+percent", textfont_color="#123B2A")
st.plotly_chart(style_chart(fig1), use_container_width=True, config={"displayModeBar": False})

# Department analysis
st.subheader("Department-wise Attrition")
dept = (
    df.groupby("Department")["Attrition"]
      .apply(lambda values: (values.str.lower() == "yes").mean() * 100)
      .reset_index(name="Attrition Rate")
)
fig2 = px.bar(
    dept, x="Department", y="Attrition Rate", color="Department",
    title="Attrition Rate by Department", text_auto=".2f",
    color_discrete_sequence=["#176B45", "#4C956C", "#91C9A8"]
)
fig2.update_traces(textposition="outside", cliponaxis=False)
st.plotly_chart(style_chart(fig2), use_container_width=True, config={"displayModeBar": False})

# Income analysis
st.subheader("Monthly Income Analysis")
fig3 = px.box(
    df, x="Attrition", y="MonthlyIncome", color="Attrition",
    title="Income Distribution by Attrition",
    color_discrete_map={"No": "#176B45", "Yes": "#91DDAF"}
)
st.plotly_chart(style_chart(fig3), use_container_width=True, config={"displayModeBar": False})

# Overtime analysis
st.subheader("Overtime and Attrition")
ot = (
    df.groupby("OverTime")["Attrition"]
      .apply(lambda values: (values.str.lower() == "yes").mean() * 100)
      .reset_index(name="Attrition Rate")
)
fig4 = px.bar(
    ot, x="OverTime", y="Attrition Rate", color="OverTime",
    title="Attrition Rate Based on Overtime", text_auto=".2f",
    color_discrete_sequence=["#176B45", "#91C9A8"]
)
fig4.update_traces(textposition="outside", cliponaxis=False)
st.plotly_chart(style_chart(fig4), use_container_width=True, config={"displayModeBar": False})

# Job satisfaction
st.subheader("Job Satisfaction Analysis")
fig5 = px.histogram(
    df, x="JobSatisfaction", color="Attrition", barmode="group",
    title="Job Satisfaction vs Attrition",
    color_discrete_map={"No": "#176B45", "Yes": "#91DDAF"}
)
st.plotly_chart(style_chart(fig5), use_container_width=True, config={"displayModeBar": False})
