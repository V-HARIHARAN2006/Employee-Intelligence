
import streamlit as st
import pandas as pd
import numpy as np
import shap
import joblib
import matplotlib.pyplot as plt
import plotly.express as px

from pathlib import Path

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================



BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "dataset" / "employee_data.csv"
MODEL_PATH = BASE_DIR / "models" / "attrition_model.pkl"

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
    font-size: 15px;
    color: #718096;
    margin-bottom: 25px;
}

.section-title {
    font-size: 21px;
    font-weight: 750;
    color: #14243B;
    margin-top: 18px;
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
# 3. PAGE HEADER
# =====================================================

st.markdown(
    '<div class="main-heading">🧠 AI Insights & Explainability</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-heading">'
    'Understand the factors influencing employee attrition '
    'using SHAP machine learning explainability.'
    '</div>',
    unsafe_allow_html=True
)

# =====================================================
# 4. LOAD DATA AND MODEL
# =====================================================

if not DATA_PATH.exists():
    st.error("Employee dataset not found.")
    st.stop()

if not MODEL_PATH.exists():
    st.error("Trained ML model not found. Run train_model.py first.")
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


@st.cache_resource
def load_model(path):
    return joblib.load(path)


try:
    df = load_data(str(DATA_PATH))
    model = load_model(str(MODEL_PATH))

except Exception as error:
    st.error(f"Unable to load project files: {error}")
    st.stop()


# =====================================================
# 5. PREPARE MODEL FEATURES
# =====================================================

feature_names = model.feature_names_in_.tolist()

missing = [
    column for column in feature_names
    if column not in df.columns
]

if missing:
    st.error(f"Missing model features in dataset: {missing}")
    st.stop()

X = df[feature_names].copy()

y = (
    df["Attrition"].map({"No": 0, "Yes": 1})
)

# =====================================================
# 6. WORKFORCE INSIGHTS
# =====================================================

st.markdown(
    '<div class="section-title">Workforce Overview</div>',
    unsafe_allow_html=True
)

total = len(df)
left = int((df["Attrition"] == "Yes").sum())
retained = int((df["Attrition"] == "No").sum())

rate = left / total * 100 if total else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Employees", f"{total:,}")
c2.metric("Employees Left", f"{left:,}")
c3.metric("Employees Retained", f"{retained:,}")
c4.metric("Attrition Rate", f"{rate:.2f}%")

st.divider()

# =====================================================
# 7. DEPARTMENT-WISE ATTRITION
# =====================================================

st.markdown(
    '<div class="section-title">Department Risk Analysis</div>',
    unsafe_allow_html=True
)

if "Department" in df.columns:

    department_data = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="Attrition Rate")
    )

    department_fig = px.bar(
        department_data,
        x="Department",
        y="Attrition Rate",
        color="Department",
        text_auto=".2f",
        title="Department-wise Employee Attrition",
        color_discrete_sequence=[
            "#2563EB",
            "#0EA5E9",
            "#6366F1"
        ]
    )

    department_fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=380,
        yaxis_title="Attrition Rate (%)"
    )

    st.plotly_chart(
        department_fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# 8. SHAP EXPLAINABILITY
# =====================================================

st.markdown(
    '<div class="section-title">SHAP Model Explainability</div>',
    unsafe_allow_html=True
)

st.write("""
SHAP explains how individual employee features contribute
to the predictions made by the trained machine learning model.

Positive SHAP values generally move the model output towards
the attrition class, while negative values move it away.
The exact interpretation depends on the model output being explained.
""")

st.info(
    "SHAP analysis can take some time because it calculates "
    "feature contributions for the selected model."
)

# =====================================================
# 9. RUN SHAP ANALYSIS
# =====================================================

if st.button(
    "Generate SHAP Analysis",
    type="primary",
    use_container_width=True
):

    try:

        with st.spinner("Calculating SHAP values..."):

            preprocessor = model.named_steps["preprocessor"]

            classifier = model.named_steps["classifier"]

            transformed = preprocessor.transform(X)

            # SHAP plotting works more reliably with dense arrays
            if hasattr(transformed, "toarray"):
                transformed = transformed.toarray()

            transformed = np.asarray(transformed)

            transformed = np.nan_to_num(
                transformed,
                nan=0.0,
                posinf=0.0,
                neginf=0.0
            )

            transformed_names = (
                preprocessor.get_feature_names_out().tolist()
            )

            rng = np.random.default_rng(42)

            background_size = min(50, len(transformed))
            explanation_size = min(100, len(transformed))

            background_indices = rng.choice(
                len(transformed),
                size=background_size,
                replace=False
            )

            explanation_indices = rng.choice(
                len(transformed),
                size=explanation_size,
                replace=False
            )

            background = transformed[background_indices]

            explanation_data = transformed[explanation_indices]

            explainer = shap.Explainer(
                classifier,
                background,
                feature_names=transformed_names
            )

            shap_result = explainer(explanation_data)

            # Handle different SHAP output formats
            shap_values = np.asarray(shap_result.values)
            base_values = np.asarray(shap_result.base_values)

            if shap_values.ndim == 3:

                # Binary classifier: select attrition class
                shap_values = shap_values[:, :, 1]

                if base_values.ndim == 2:
                    base_values = base_values[:, 1]

            elif shap_values.ndim == 1:

                shap_values = shap_values.reshape(1, -1)

            # Store analysis in session
            st.session_state["shap_values"] = shap_values
            st.session_state["shap_base_values"] = base_values
            st.session_state["shap_data"] = explanation_data
            st.session_state["shap_names"] = transformed_names
            st.session_state["shap_indices"] = explanation_indices

            st.success("SHAP analysis completed successfully!")

    except Exception as error:

        st.error(f"SHAP calculation failed: {error}")

        st.info(
            "Check that the trained model is available and "
            "that the SHAP library is installed correctly."
        )

# =====================================================
# 10. DISPLAY SHAP RESULTS
# =====================================================

if "shap_values" in st.session_state:

    shap_values = st.session_state["shap_values"]

    shap_base_values = st.session_state["shap_base_values"]

    shap_data = st.session_state["shap_data"]

    shap_names = st.session_state["shap_names"]

    shap_indices = st.session_state["shap_indices"]

    # -------------------------------------------------
    # GLOBAL FEATURE IMPORTANCE
    # -------------------------------------------------

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Global Feature Importance'
        '</div>',
        unsafe_allow_html=True
    )

    importance = np.mean(
        np.abs(shap_values),
        axis=0
    )

    importance_df = pd.DataFrame({
        "Feature": shap_names,
        "Mean Absolute SHAP": importance
    }).sort_values(
        "Mean Absolute SHAP",
        ascending=False
    ).head(15)

    importance_fig = px.bar(
        importance_df.sort_values(
            "Mean Absolute SHAP",
            ascending=True
        ),
        x="Mean Absolute SHAP",
        y="Feature",
        orientation="h",
        title="Top 15 Features Influencing Model Predictions",
        color="Mean Absolute SHAP",
        color_continuous_scale="Blues"
    )

    importance_fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=550
    )

    st.plotly_chart(
        importance_fig,
        use_container_width=True
    )

    st.caption(
        "Mean absolute SHAP measures average contribution magnitude. "
        "It does not indicate whether a feature increases or decreases risk."
    )

    # -------------------------------------------------
    # INDIVIDUAL EMPLOYEE EXPLANATION
    # -------------------------------------------------

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Individual Employee Explanation'
        '</div>',
        unsafe_allow_html=True
    )

    selected_position = st.selectbox(
        "Select an employee record to explain",
        range(len(shap_indices)),
        format_func=lambda i: (
            f"Employee record {int(shap_indices[i]) + 1} "
            f"({df.iloc[int(shap_indices[i])]['Attrition']})"
        )
    )

    actual_index = int(shap_indices[selected_position])

    employee_shap = shap_values[selected_position]

    base = np.asarray(shap_base_values)

    if base.ndim == 0:
        base_value = float(base)

    elif base.ndim == 1:
        base_value = float(base[selected_position])

    else:
        base_value = float(base[selected_position].ravel()[0])

    employee_explanation = shap.Explanation(
        values=employee_shap,
        base_values=base_value,
        data=shap_data[selected_position],
        feature_names=shap_names
    )

    employee_row = df.iloc[actual_index]

    predicted_probability = model.predict_proba(
        X.iloc[[actual_index]]
    )[0][1]

    prediction = model.predict(
        X.iloc[[actual_index]]
    )[0]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Actual Attrition",
            employee_row["Attrition"]
        )

    with col2:

        st.metric(
            "Model Attrition Probability",
            f"{predicted_probability * 100:.2f}%"
        )

    st.write(
        "Model Prediction:",
        "Attrition" if prediction == 1 else "No Attrition"
    )

    st.write("### SHAP Waterfall Explanation")

    fig, ax = plt.subplots(figsize=(11, 7))

    shap.plots.waterfall(
        employee_explanation,
        max_display=12,
        show=False
    )

    plt.tight_layout()

    st.pyplot(
        plt.gcf(),
        use_container_width=True
    )

    plt.close()

    st.caption(
        "The waterfall plot explains the selected model's output. "
        "For tree models this may be in raw-score space rather than "
        "probability space."
    )

    # -------------------------------------------------
    # TOP INDIVIDUAL CONTRIBUTIONS
    # -------------------------------------------------

    st.subheader("Strongest Individual Feature Contributions")

    individual_df = pd.DataFrame({
        "Feature": shap_names,
        "SHAP Contribution": employee_shap
    })

    individual_df["Absolute Contribution"] = (
        individual_df["SHAP Contribution"].abs()
    )

    individual_df = individual_df.sort_values(
        "Absolute Contribution",
        ascending=False
    ).head(10)

    individual_df["Direction"] = np.where(
        individual_df["SHAP Contribution"] > 0,
        "Toward Attrition",
        "Away from Attrition"
    )

    st.dataframe(
        individual_df[
            [
                "Feature",
                "SHAP Contribution",
                "Direction"
            ]
        ].style.format({
            "SHAP Contribution": "{:.4f}"
        }),
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# 11. AUTOMATED WORKFORCE OBSERVATIONS
# =====================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    'Automated Workforce Observations'
    '</div>',
    unsafe_allow_html=True
)

recommendations = []

if "OverTime" in df.columns:

    overtime_rate = (
        df[df["OverTime"] == "Yes"]["Attrition"] == "Yes"
    ).mean() * 100

    normal_rate = (
        df[df["OverTime"] == "No"]["Attrition"] == "Yes"
    ).mean() * 100

    if overtime_rate > normal_rate:

        recommendations.append(
            (
                "Overtime",
                f"Overtime employees have an observed attrition "
                f"rate of {overtime_rate:.2f}% compared with "
                f"{normal_rate:.2f}% for non-overtime employees. "
                "Review workload and staffing distribution."
            )
        )

if "JobSatisfaction" in df.columns:

    low_rate = (
        df[df["JobSatisfaction"] <= 2]["Attrition"] == "Yes"
    ).mean() * 100

    high_rate = (
        df[df["JobSatisfaction"] >= 3]["Attrition"] == "Yes"
    ).mean() * 100

    if low_rate > high_rate:

        recommendations.append(
            (
                "Job Satisfaction",
                f"Employees with lower job satisfaction have an "
                f"observed attrition rate of {low_rate:.2f}%, "
                f"compared with {high_rate:.2f}% for the other group. "
                "Consider employee feedback and engagement initiatives."
            )
        )

if "WorkLifeBalance" in df.columns:

    low_balance = (
        df[df["WorkLifeBalance"] <= 2]["Attrition"] == "Yes"
    ).mean() * 100

    recommendations.append(
        (
            "Work-Life Balance",
            f"The observed attrition rate among employees with "
            f"work-life balance scores of 1 or 2 is "
            f"{low_balance:.2f}%. Review flexible work options."
        )
    )

if "YearsSinceLastPromotion" in df.columns:

    promotion_group = df[
        df["YearsSinceLastPromotion"] >= 4
    ]

    if len(promotion_group) > 0:

        promotion_rate = (
            promotion_group["Attrition"] == "Yes"
        ).mean() * 100

        recommendations.append(
            (
                "Career Progression",
                f"Employees with four or more years since their "
                f"last promotion have an observed attrition rate "
                f"of {promotion_rate:.2f}%. Review career development "
                "and advancement opportunities."
            )
        )

if recommendations:

    for title, description in recommendations:

        with st.expander(title):

            st.write(description)

else:

    st.info(
        "No observations were generated from the selected rules."
    )

st.caption(
    "These are descriptive associations from the sample dataset, "
    "not proof of causation or personalized employment advice."
)

# =====================================================
# 12. FOOTER
# =====================================================

st.divider()

st.markdown("""
<div style="text-align:center;color:#718096;
font-size:12px;padding:20px;">

<b>EMPLOYEE INTELLIGENCE</b><br><br>

AI-Powered Workforce Analytics<br>

Employee Attrition Prediction Using Machine Learning

</div>
""", unsafe_allow_html=True)
