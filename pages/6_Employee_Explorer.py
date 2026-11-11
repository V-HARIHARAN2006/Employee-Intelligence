
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================



BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "dataset" / "employee_data.csv"
MODEL_PATH = BASE_DIR / "models" / "attrition_model.pkl"

# ==========================================================
# 2. THEME
# ==========================================================

st.markdown("""
<style>

.stApp {
    background-color: #EFFFF2;
    color: #3D4841;
    font-family: Georgia, "Times New Roman", serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background-color: #D0F5DC;
}

[data-testid="stSidebar"] * {
    color: #3D4841;
    font-family: Georgia, serif;
}

#MainMenu, footer {
    visibility: hidden;
}

.explorer-header {
    background: #91E3AF;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    color: #3D4841;
    font-family: Georgia, serif;
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 15px;
}

.explorer-subtitle {
    color: #718477;
    font-size: 14px;
    margin-bottom: 20px;
}

.employee-card {
    background: #D0F5DC;
    border: 1px solid #668F75;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    box-shadow: 3px 5px 10px rgba(45,80,55,0.15);
}

.employee-number {
    font-size: 28px;
    font-weight: bold;
    color: #3D4841;
}

.employee-label {
    color: #40554A;
    font-size: 13px;
    font-weight: bold;
}

div[data-testid="stMetric"] {
    background: #D0F5DC;
    border: 1px solid #668F75;
    border-radius: 12px;
    padding: 14px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #F6FFF7;
    border: 1px solid #A3BBA8;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# 3. HEADER
# ==========================================================

st.markdown("""
<div class="explorer-header">
    EMPLOYEE EXPLORER
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="explorer-subtitle">
    Search, analyse and explore employee records with
    AI-powered attrition prediction.
</div>
""", unsafe_allow_html=True)

# ==========================================================
# 4. LOAD DATA
# ==========================================================

if not DATA_PATH.exists():
    st.error("Employee dataset not found.")
    st.code(str(DATA_PATH))
    st.stop()


@st.cache_data
def load_data(path):

    data = pd.read_csv(path)

    data.columns = data.columns.str.strip()

    if "Attrition" in data.columns:
        data["Attrition"] = (
            data["Attrition"]
            .astype(str)
            .str.strip()
            .str.capitalize()
        )

    if "Gender" in data.columns:
        data["Gender"] = (
            data["Gender"]
            .astype(str)
            .str.strip()
            .str.capitalize()
        )

    return data


@st.cache_resource
def load_model(path):
    return joblib.load(path)


try:
    df = load_data(str(DATA_PATH))
except Exception as error:
    st.error(f"Dataset loading error: {error}")
    st.stop()

if "Attrition" not in df.columns:
    st.error("The dataset does not contain an Attrition column.")
    st.stop()

# ==========================================================
# 5. EMPLOYEE IDENTIFIER
# ==========================================================

if "EmployeeNumber" in df.columns:
    df["_EmployeeID"] = df["EmployeeNumber"].astype(str)
else:
    df["_EmployeeID"] = (
        df.index + 1
    ).astype(str)

# ==========================================================
# 6. EMPLOYEE OVERVIEW
# ==========================================================

total = len(df)

active = int(
    (df["Attrition"] == "No").sum()
)

left = int(
    (df["Attrition"] == "Yes").sum()
)

rate = (
    left / total * 100 if total else 0
)

st.subheader("Employee Database Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Employees", f"{total:,}")
c2.metric("Active Employees", f"{active:,}")
c3.metric("Employees Left", f"{left:,}")
c4.metric("Attrition Rate", f"{rate:.2f}%")

st.divider()

# ==========================================================
# 7. SEARCH AND FILTERS
# ==========================================================

st.subheader("Search and Filter Employees")

search = st.text_input(
    "Search employee",
    placeholder="Enter employee ID, job role, department or other details..."
)

filter_cols = st.columns(4)

# Gender
if "Gender" in df.columns:

    with filter_cols[0]:

        gender_options = ["All"] + sorted(
            df["Gender"].dropna().unique().tolist()
        )

        gender_filter = st.selectbox(
            "Gender",
            gender_options
        )

else:
    gender_filter = "All"

# Department
if "Department" in df.columns:

    with filter_cols[1]:

        department_options = ["All"] + sorted(
            df["Department"].dropna().unique().tolist()
        )

        department_filter = st.selectbox(
            "Department",
            department_options
        )

else:
    department_filter = "All"

# Job role
if "JobRole" in df.columns:

    with filter_cols[2]:

        role_options = ["All"] + sorted(
            df["JobRole"].dropna().unique().tolist()
        )

        role_filter = st.selectbox(
            "Job Role",
            role_options
        )

else:
    role_filter = "All"

# Attrition
with filter_cols[3]:

    attrition_filter = st.selectbox(
        "Attrition Status",
        ["All", "No", "Yes"]
    )

# ==========================================================
# 8. APPLY FILTERS
# ==========================================================

filtered = df.copy()

if gender_filter != "All":
    filtered = filtered[
        filtered["Gender"] == gender_filter
    ]

if department_filter != "All":
    filtered = filtered[
        filtered["Department"] == department_filter
    ]

if role_filter != "All":
    filtered = filtered[
        filtered["JobRole"] == role_filter
    ]

if attrition_filter != "All":
    filtered = filtered[
        filtered["Attrition"] == attrition_filter
    ]

if search.strip():

    mask = filtered.astype(str).apply(
        lambda column: column.str.contains(
            search.strip(),
            case=False,
            na=False,
            regex=False
        )
    ).any(axis=1)

    filtered = filtered[mask]

# ==========================================================
# 9. FILTERED EMPLOYEE RESULTS
# ==========================================================

st.divider()

st.subheader("Employee Records")

st.caption(
    f"Showing {len(filtered):,} employees out of {total:,} records."
)

display_columns = [
    column for column in [
        "_EmployeeID",
        "Age",
        "Gender",
        "Department",
        "JobRole",
        "MonthlyIncome",
        "JobSatisfaction",
        "YearsAtCompany",
        "OverTime",
        "Attrition"
    ]
    if column in filtered.columns
]

display_df = filtered[display_columns].rename(
    columns={
        "_EmployeeID": "Employee ID"
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=350
)

# ==========================================================
# 10. DOWNLOAD FILTERED DATA
# ==========================================================

csv_data = filtered.drop(
    columns=["_EmployeeID"],
    errors="ignore"
).to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Employee Records",
    data=csv_data,
    file_name="filtered_employee_records.csv",
    mime="text/csv",
    use_container_width=True
)

# ==========================================================
# 11. INDIVIDUAL EMPLOYEE PROFILE
# ==========================================================

st.divider()

st.subheader("Individual Employee Profile")

if filtered.empty:

    st.warning("No employee records match your filters.")

else:

    employee_ids = filtered["_EmployeeID"].tolist()

    selected_id = st.selectbox(
        "Select Employee ID",
        employee_ids
    )

    employee = filtered[
        filtered["_EmployeeID"] == selected_id
    ].iloc[0]

    st.markdown(
        f"""
        <div class="employee-card">
            <div class="employee-number">
                Employee #{selected_id}
            </div>
            <div class="employee-label">
                EMPLOYEE PROFILE
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # Employee information
    profile_fields = [
        ("Age", "Age"),
        ("Gender", "Gender"),
        ("Department", "Department"),
        ("Job Role", "JobRole"),
        ("Monthly Income", "MonthlyIncome"),
        ("Job Satisfaction", "JobSatisfaction"),
        ("Work-Life Balance", "WorkLifeBalance"),
        ("Years at Company", "YearsAtCompany"),
        ("Years in Current Role", "YearsInCurrentRole"),
        ("Years Since Last Promotion", "YearsSinceLastPromotion"),
        ("Overtime", "OverTime"),
        ("Business Travel", "BusinessTravel"),
        ("Education", "Education"),
        ("Performance Rating", "PerformanceRating")
    ]

    profile_cols = st.columns(3)

    visible_fields = [
        (label, column)
        for label, column in profile_fields
        if column in df.columns
    ]

    for index, (label, column) in enumerate(visible_fields):

        with profile_cols[index % 3]:

            value = employee[column]

            if pd.isna(value):
                value = "Not Available"

            elif column == "MonthlyIncome":
                value = f"{float(value):,.0f}"

            st.metric(
                label,
                str(value)
            )

    # Actual attrition status
    st.write("")

    if employee["Attrition"] == "Yes":
        st.error("Actual Attrition Status: Employee Left")
    else:
        st.success("Actual Attrition Status: Employee Retained")

# ==========================================================
# 12. AI ATTRITION PREDICTION
# ==========================================================

st.divider()

st.subheader("AI Employee Attrition Prediction")

st.write(
    "Use the trained machine learning model to estimate "
    "the selected employee's attrition probability."
)

if not filtered.empty:

    if not MODEL_PATH.exists():

        st.warning(
            "Trained model not found. Run train_model.py first."
        )

    else:

        if st.button(
            "Predict Employee Attrition",
            type="primary",
            use_container_width=True
        ):

            try:

                model = load_model(str(MODEL_PATH))

                feature_names = (
                    model.feature_names_in_.tolist()
                )

                missing_features = [
                    col for col in feature_names
                    if col not in df.columns
                ]

                if missing_features:

                    st.error(
                        f"Missing model features: {missing_features}"
                    )

                else:

                    prediction_input = pd.DataFrame(
                        [
                            employee[feature_names].to_dict()
                        ],
                        columns=feature_names
                    )

                    prediction = int(
                        model.predict(prediction_input)[0]
                    )

                    probability = float(
                        model.predict_proba(
                            prediction_input
                        )[0][1]
                    )

                    result1, result2 = st.columns(2)

                    with result1:

                        st.metric(
                            "Attrition Probability",
                            f"{probability * 100:.2f}%"
                        )

                    with result2:

                        st.metric(
                            "Model Prediction",
                            "Likely to Leave" if prediction == 1
                            else "Likely to Stay"
                        )

                    st.progress(probability)

                    if probability >= 0.60:

                        st.error(
                            "High predicted attrition probability. "
                            "Consider a supportive HR review."
                        )

                    elif probability >= 0.30:

                        st.warning(
                            "Moderate predicted attrition probability. "
                            "Monitor engagement and employee feedback."
                        )

                    else:

                        st.success(
                            "Low predicted attrition probability."
                        )

                    st.caption(
                        "This is a model estimate, not a certainty. "
                        "It should not be used as the sole basis for "
                        "employment decisions."
                    )

            except Exception as error:

                st.error(
                    f"Prediction failed: {error}"
                )

# ==========================================================
# 13. FOOTER
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

    EMPLOYEE INTELLIGENCE<br><br>

    Employee Explorer & AI Attrition Prediction<br>

    Data Science and Machine Learning Project

</div>
""", unsafe_allow_html=True)
