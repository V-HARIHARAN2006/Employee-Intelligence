
import streamlit as st
import pandas as pd
import plotly.express as px



st.title("📊 Workforce Analytics")
st.caption("Analyze employee trends and attrition patterns")

df = pd.read_csv("dataset/employee_data.csv")

# Attrition distribution
st.subheader("Employee Attrition Distribution")

attrition_counts = df["Attrition"].value_counts().reset_index()
attrition_counts.columns = ["Attrition", "Employees"]

fig1 = px.pie(
    attrition_counts,
    names="Attrition",
    values="Employees",
    hole=0.55,
    title="Employees: Stayed vs Left"
)

st.plotly_chart(fig1, use_container_width=True)

# Department analysis
st.subheader("Department-wise Attrition")

dept = (
    df.groupby("Department")["Attrition"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .reset_index(name="Attrition Rate")
)

fig2 = px.bar(
    dept,
    x="Department",
    y="Attrition Rate",
    color="Department",
    title="Attrition Rate by Department",
    text_auto=".2f"
)

st.plotly_chart(fig2, use_container_width=True)

# Income analysis
st.subheader("Monthly Income Analysis")

fig3 = px.box(
    df,
    x="Attrition",
    y="MonthlyIncome",
    color="Attrition",
    title="Income Distribution by Attrition"
)

st.plotly_chart(fig3, use_container_width=True)

# Overtime analysis
st.subheader("Overtime and Attrition")

ot = (
    df.groupby("OverTime")["Attrition"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .reset_index(name="Attrition Rate")
)

fig4 = px.bar(
    ot,
    x="OverTime",
    y="Attrition Rate",
    color="OverTime",
    title="Attrition Rate Based on Overtime",
    text_auto=".2f"
)

st.plotly_chart(fig4, use_container_width=True)

# Job satisfaction
st.subheader("Job Satisfaction Analysis")

fig5 = px.histogram(
    df,
    x="JobSatisfaction",
    color="Attrition",
    barmode="group",
    title="Job Satisfaction vs Attrition"
)

st.plotly_chart(fig5, use_container_width=True)
